"""
Fallback Handler - Automatic failover on provider failures
Part of Smart Router for 75-80% reliability
"""

import time
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading


class FailureType(Enum):
    """Types of failures that trigger fallback."""
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    TIMEOUT = "timeout"
    SERVER_ERROR = "server_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


@dataclass
class FallbackRule:
    """Rule for fallback behavior."""
    when: FailureType
    wait_seconds: int = 30
    switch_provider: bool = True
    reduce_model_size: bool = False
    max_retries: int = 3


@dataclass
class ProviderHealth:
    """Health status of a provider."""
    name: str
    is_healthy: bool = True
    consecutive_failures: int = 0
    last_failure_time: float = 0
    cooldown_until: float = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


class FallbackHandler:
    """
    Handles automatic fallback when providers fail.
    Ensures 75-80% success rate through intelligent failover.
    """
    
    # Default fallback rules
    DEFAULT_RULES = [
        FallbackRule(
            when=FailureType.RATE_LIMIT,
            wait_seconds=60,
            switch_provider=True,
            max_retries=5
        ),
        FallbackRule(
            when=FailureType.AUTH_ERROR,
            wait_seconds=300,
            switch_provider=True,
            max_retries=1
        ),
        FallbackRule(
            when=FailureType.TIMEOUT,
            wait_seconds=30,
            switch_provider=True,
            max_retries=3
        ),
        FallbackRule(
            when=FailureType.SERVER_ERROR,
            wait_seconds=60,
            switch_provider=True,
            max_retries=3
        ),
        FallbackRule(
            when=FailureType.NETWORK_ERROR,
            wait_seconds=30,
            switch_provider=False,
            max_retries=3
        ),
    ]
    
    def __init__(self, router):
        self.router = router
        self.provider_health: Dict[str, ProviderHealth] = {}
        self.rules = {rule.when: rule for rule in self.DEFAULT_RULES}
        self._lock = threading.Lock()
        self.retry_history: List[Dict] = []
        self.current_attempt = 0
        self.max_attempts = 10
    
    def _classify_failure(self, error: str) -> FailureType:
        """Classify an error into a failure type."""
        error_lower = error.lower()
        
        if "rate limit" in error_lower or "429" in error_lower:
            return FailureType.RATE_LIMIT
        elif "unauthorized" in error_lower or "401" in error_lower or "403" in error_lower:
            return FailureType.AUTH_ERROR
        elif "timeout" in error_lower or "timed out" in error_lower:
            return FailureType.TIMEOUT
        elif "500" in error_lower or "502" in error_lower or "503" in error_lower or "server error" in error_lower:
            return FailureType.SERVER_ERROR
        elif "connection" in error_lower or "network" in error_lower or "ECONNREFUSED" in error_lower:
            return FailureType.NETWORK_ERROR
        else:
            return FailureType.UNKNOWN
    
    def _mark_provider_down(self, provider_name: str, failure_type: FailureType):
        """Mark a provider as unhealthy."""
        if provider_name not in self.provider_health:
            self.provider_health[provider_name] = ProviderHealth(name=provider_name)
        
        with self.provider_health[provider_name].lock:
            health = self.provider_health[provider_name]
            health.consecutive_failures += 1
            health.last_failure_time = time.time()
            
            if health.consecutive_failures >= 3:
                rule = self.rules.get(failure_type, self.DEFAULT_RULES[-1])
                health.is_healthy = False
                health.cooldown_until = time.time() + rule.wait_seconds
    
    def _mark_provider_up(self, provider_name: str):
        """Mark a provider as healthy again."""
        if provider_name in self.provider_health:
            with self.provider_health[provider_name].lock:
                health = self.provider_health[provider_name]
                health.is_healthy = True
                health.consecutive_failures = 0
    
    def _should_fallback(self, provider_name: str) -> bool:
        """Check if we should fallback from this provider."""
        if provider_name not in self.provider_health:
            return False
        
        health = self.provider_health[provider_name]
        
        with health.lock:
            if not health.is_healthy:
                if time.time() < health.cooldown_until:
                    return True
                else:
                    health.is_healthy = True
            
            return False
    
    def _get_fallback_model(self, current_model: str, provider: str) -> Optional[str]:
        """Get a smaller/faster model for fallback."""
        # Model size reduction mappings
        fallbacks = {
            "llama-3.3-70b-versatile": "llama-3.1-8b-instant",
            "qwen/qwen3-32b": "qwen/qwen3-30b",
            "qwen/qwen3-next-80b-a3b-instruct:free": "qwen/qwen3-coder:free",
        }
        return fallbacks.get(current_model)
    
    def _record_retry(self, provider: str, model: str, error: str, attempt: int):
        """Record retry attempt."""
        with self._lock:
            self.retry_history.append({
                "timestamp": time.time(),
                "provider": provider,
                "model": model,
                "error": error[:200],  # Truncate
                "attempt": attempt,
            })
            # Keep only last 100 retries
            self.retry_history = self.retry_history[-100:]
    
    def execute_with_fallback(
        self,
        callback: Callable,
        on_failure: Optional[Callable] = None,
        max_attempts: int = 5,
    ) -> Dict[str, Any]:
        """
        Execute a callback with automatic fallback on failure.
        
        Args:
            callback: Function to call with (provider, model)
            on_failure: Optional callback on final failure
            
        Returns:
            Dict with result or error
        """
        self.current_attempt = 0
        last_error = "Unknown error"
        
        while self.current_attempt < max_attempts:
            self.current_attempt += 1
            
            try:
                result = callback()
                
                if "error" not in result:
                    # Success! Reset state
                    if self.current_attempt > 1:
                        self._mark_provider_up(result.get("provider", "unknown"))
                    return result
                
                last_error = result["error"]
                failure_type = self._classify_failure(last_error)
                
                # Record the retry
                provider = result.get("provider", "unknown")
                model = result.get("model", "unknown")
                self._record_retry(provider, model, last_error, self.current_attempt)
                
                # Mark provider as potentially down
                if provider != "unknown":
                    self._mark_provider_down(provider, failure_type)
                
                # Apply fallback rule
                rule = self.rules.get(failure_type, self.DEFAULT_RULES[-1])
                
                # Check retry limit
                if self.current_attempt >= rule.max_retries:
                    if on_failure:
                        on_failure(last_error)
                    return {
                        "error": f"Max retries ({rule.max_retries}) reached: {last_error}",
                        "attempts": self.current_attempt,
                        "failure_type": failure_type.value,
                    }
                
                # Wait before retry
                time.sleep(rule.wait_seconds)
                
            except Exception as e:
                last_error = str(e)
                self._record_retry("unknown", "unknown", last_error, self.current_attempt)
                
                if self.current_attempt >= max_attempts:
                    return {
                        "error": f"Max attempts reached: {last_error}",
                        "attempts": self.current_attempt,
                    }
                
                time.sleep(5)
        
        return {
            "error": f"Failed after {self.current_attempt} attempts: {last_error}",
            "attempts": self.current_attempt,
        }
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get health status of all providers."""
        report = {
            "providers": {},
            "summary": {
                "healthy": 0,
                "unhealthy": 0,
                "in_cooldown": 0,
            },
            "recent_failures": self.retry_history[-10:] if self.retry_history else [],
        }
        
        for name, health in self.provider_health.items():
            with health.lock:
                in_cooldown = time.time() < health.cooldown_until
                status = "healthy"
                if in_cooldown:
                    status = "in_cooldown"
                elif not health.is_healthy:
                    status = "unhealthy"
                
                report["providers"][name] = {
                    "status": status,
                    "consecutive_failures": health.consecutive_failures,
                    "last_failure": health.last_failure_time,
                    "cooldown_remaining": max(0, health.cooldown_until - time.time()) if in_cooldown else 0,
                }
                
                if status == "healthy":
                    report["summary"]["healthy"] += 1
                elif status == "in_cooldown":
                    report["summary"]["in_cooldown"] += 1
                else:
                    report["summary"]["unhealthy"] += 1
        
        return report
    
    def clear_health(self, provider_name: Optional[str] = None):
        """Clear health status for a provider or all providers."""
        if provider_name:
            if provider_name in self.provider_health:
                del self.provider_health[provider_name]
        else:
            self.provider_health.clear()
        self.retry_history.clear()


def create_fallback_handler(router) -> FallbackHandler:
    """Create a fallback handler with the given router."""
    return FallbackHandler(router)
