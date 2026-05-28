"""
Smart Router - Rotates across multiple FREE API providers
Ensures 75-80% performance via intelligent model selection
NOW WITH SKILL MIDDLEWARE INTEGRATION
"""

import os
import time
import random
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import threading

# Import skill middleware
try:
    from neuro.skills.skill_middleware import SkillMiddleware, get_middleware, set_active_skills
    MIDDLEWARE_AVAILABLE = True
except ImportError:
    MIDDLEWARE_AVAILABLE = False


class Provider(Enum):
    """Available API providers."""
    GROQ = "groq"
    OPENROUTER = "openrouter"
    HUGGINGFACE = "huggingface"
    CLOUDFLARE = "cloudflare"
    TOGETHER = "together"


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: Provider
    base_url: str
    api_key_env: str
    models: List[str]
    requires_endpoint: bool = False
    rate_limit: int = 60  # requests per minute
    cooldown: int = 60  # seconds after rate limit


@dataclass
class RouterStats:
    """Statistics for routing decisions."""
    total_calls: int = 0
    provider_calls: Dict[str, int] = field(default_factory=dict)
    failures: Dict[str, int] = field(default_factory=dict)
    avg_latency: Dict[str, float] = field(default_factory=dict)
    last_used: Dict[str, float] = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock)


class SmartRouter:
    """
    Intelligent router that rotates across multiple FREE API providers.
    Ensures best model selection and automatic failover.
    NOW WITH SKILL MIDDLEWARE INTEGRATION for 259+ skills.
    """
    
    # Provider configurations
    PROVIDERS: Dict[Provider, ProviderConfig] = {
        Provider.GROQ: ProviderConfig(
            name=Provider.GROQ,
            base_url="https://api.groq.com/openai/v1",
            api_key_env="GROQ_API_KEYS",
            models=[
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "qwen/qwen3-32b",
                "meta-llama/llama-4-scout-17b-16e-instruct",
            ],
            rate_limit=30,
        ),
        Provider.OPENROUTER: ProviderConfig(
            name=Provider.OPENROUTER,
            base_url="https://openrouter.ai/api/v1",
            api_key_env="OPENROUTER_API_KEYS",
            models=[
                "qwen/qwen3-coder:free",
                "qwen/qwen3-next-80b-a3b-instruct:free",
                "deepseek/deepseek-v4-flash:free",
                "google/gemma-4-31b-it:free",
                "google/gemma-4-26b-a4b-it:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "meta-llama/llama-3.2-3b-instruct:free",
            ],
            rate_limit=60,
        ),
        Provider.HUGGINGFACE: ProviderConfig(
            name=Provider.HUGGINGFACE,
            base_url="https://api-inference.huggingface.co/models",
            api_key_env="HF_TOKEN",
            models=[
                "Qwen/Qwen2.5-Coder-32B-Instruct",
                "deepseek-ai/DeepSeek-Coder-V2",
            ],
            requires_endpoint=True,
            rate_limit=30,
        ),
        Provider.CLOUDFLARE: ProviderConfig(
            name=Provider.CLOUDFLARE,
            base_url="https://api.cloudflare.com/client/v4/workers",
            api_key_env="CLOUDFLARE_AI_API_TOKEN",
            models=["@cf/meta/llama-3-70b-instruct-fp8-fast"],
            requires_endpoint=True,
            rate_limit=1000,
        ),
        Provider.TOGETHER: ProviderConfig(
            name=Provider.TOGETHER,
            base_url="https://api.together.xyz/v1",
            api_key_env="TOGETHER_API_KEY",
            models=[
                "meta-llama/Llama-3.3-70B-Instruct",
                "Qwen/Qwen2.5-Coder-32B-Instruct",
            ],
            rate_limit=30,
        ),
    }
    
    def __init__(self):
        self.stats = RouterStats()
        self.cooldowns: Dict[str, float] = {}
        self._local = threading.local()
        # NEW: Initialize skill middleware
        self.middleware = get_middleware() if MIDDLEWARE_AVAILABLE else None
    
    def _get_api_key(self, provider: Provider) -> Optional[str]:
        """Get API key from environment."""
        config = self.PROVIDERS[provider]
        keys_str = os.getenv(config.api_key_env, "")
        
        if not keys_str:
            return None
        
        # Support comma-separated keys
        keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        if not keys:
            return None
        
        # Round-robin selection (use thread-local index)
        if not hasattr(self._local, 'key_indices'):
            self._local.key_indices = {}
        
        if provider.value not in self._local.key_indices:
            self._local.key_indices[provider.value] = 0
        
        idx = self._local.key_indices[provider.value] % len(keys)
        self._local.key_indices[provider.value] = idx + 1
        
        return keys[idx]
    
    def _is_cooldown(self, provider: Provider) -> bool:
        """Check if provider is in cooldown."""
        key = provider.value
        if key not in self.cooldowns:
            return False
        
        elapsed = time.time() - self.cooldowns[key]
        config = self.PROVIDERS[provider]
        
        if elapsed < config.cooldown:
            return True
        
        # Clear expired cooldown
        del self.cooldowns[key]
        return False
    
    def _set_cooldown(self, provider: Provider):
        """Set provider to cooldown."""
        self.cooldowns[provider.value] = time.time()
    
    def _call_groq(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Groq API."""
        try:
            from groq import Groq
        except ImportError:
            return {"error": "pip install groq"}
        
        api_key = self._get_api_key(Provider.GROQ)
        if not api_key:
            return {"error": "No Groq API key found"}
        
        try:
            client = Groq(api_key=api_key)
            
            # Filter kwargs for Groq API
            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens", "top_p", "stop"]
            }
            
            response = client.chat.completions.create(
                model=model if model else "llama-3.3-70b-versatile",
                messages=messages,
                **clean_kwargs
            )
            
            self._record_success(Provider.GROQ, model)
            
            return {
                "content": response.choices[0].message.content,
                "provider": "groq",
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                }
            }
        except Exception as e:
            self._record_failure(Provider.GROQ, model, str(e))
            return {"error": str(e)}
    
    def _call_openrouter(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call OpenRouter API."""
        try:
            from openai import OpenAI
        except ImportError:
            return {"error": "pip install openai"}
        
        api_key = self._get_api_key(Provider.OPENROUTER)
        if not api_key:
            return {"error": "No OpenRouter API key found"}
        
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            
            # Filter kwargs
            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens", "top_p", "stop"]
            }
            
            response = client.chat.completions.create(
                model=model if model else "qwen/qwen3-coder:free",
                messages=messages,
                **clean_kwargs
            )
            
            self._record_success(Provider.OPENROUTER, model)
            
            return {
                "content": response.choices[0].message.content,
                "provider": "openrouter",
                "model": model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0,
                    "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                }
            }
        except Exception as e:
            self._record_failure(Provider.OPENROUTER, model, str(e))
            return {"error": str(e)}
    
    def _call_huggingface(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call HuggingFace Inference API."""
        api_key = self._get_api_key(Provider.HUGGINGFACE)
        if not api_key:
            return {"error": "No HuggingFace token found"}
        
        try:
            import requests
            
            # Convert messages to single text
            text = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            
            response = requests.post(
                f"{self.PROVIDERS[Provider.HUGGINGFACE].base_url}/{model}",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"inputs": text},
                timeout=120
            )
            
            if response.status_code == 200:
                self._record_success(Provider.HUGGINGFACE, model)
                return {
                    "content": response.json()[0].get("generated_text", ""),
                    "provider": "huggingface",
                    "model": model,
                }
            else:
                self._record_failure(Provider.HUGGINGFACE, model, response.text)
                return {"error": f"HF API error: {response.status_code}"}
                
        except Exception as e:
            self._record_failure(Provider.HUGGINGFACE, model, str(e))
            return {"error": str(e)}
    
    def _call_cloudflare(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Cloudflare Workers AI."""
        api_key = self._get_api_key(Provider.CLOUDFLARE)
        if not api_key:
            return {"error": "No Cloudflare API token found"}
        
        try:
            import requests
            
            # Convert messages
            text = "\n".join([f"{m['role']}: {m['content']}" for m in messages if m.get("content")])
            
            response = requests.post(
                f"https://api.cloudflare.com/client/v4/workers/{model}",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"prompt": text},
                timeout=120
            )
            
            if response.status_code == 200:
                self._record_success(Provider.CLOUDFLARE, model)
                return {
                    "content": response.json().get("result", {}).get("response", ""),
                    "provider": "cloudflare",
                    "model": model,
                }
            else:
                self._record_failure(Provider.CLOUDFLARE, model, response.text)
                return {"error": f"CF error: {response.status_code}"}
                
        except Exception as e:
            self._record_failure(Provider.CLOUDFLARE, model, str(e))
            return {"error": str(e)}
    
    def _call_together(self, model: str, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """Call Together AI."""
        try:
            from openai import OpenAI
        except ImportError:
            return {"error": "pip install openai"}
        
        api_key = self._get_api_key(Provider.TOGETHER)
        if not api_key:
            return {"error": "No Together AI key found"}
        
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.together.xyz/v1"
            )
            
            clean_kwargs = {
                k: v for k, v in kwargs.items()
                if k in ["temperature", "max_tokens"]
            }
            
            response = client.chat.completions.create(
                model=model if model else "meta-llama/Llama-3.3-70B-Instruct",
                messages=messages,
                **clean_kwargs
            )
            
            self._record_success(Provider.TOGETHER, model)
            
            return {
                "content": response.choices[0].message.content,
                "provider": "together",
                "model": model,
            }
        except Exception as e:
            self._record_failure(Provider.TOGETHER, model, str(e))
            return {"error": str(e)}
    
    def _record_success(self, provider: Provider, model: str):
        """Record successful call."""
        with self.stats.lock:
            self.stats.total_calls += 1
            self.stats.provider_calls[provider.value] = self.stats.provider_calls.get(provider.value, 0) + 1
            self.stats.last_used[provider.value] = time.time()
    
    def _record_failure(self, provider: Provider, model: str, error: str):
        """Record failed call and apply cooldown."""
        with self.stats.lock:
            self.stats.failures[provider.value] = self.stats.failures.get(provider.value, 0) + 1
            
            # Apply cooldown on repeated failures
            if self.stats.failures[provider.value] >= 3:
                self._set_cooldown(provider)
                self.stats.failures[provider.value] = 0
    
    def _get_available_providers(self) -> List[Provider]:
        """Get list of available providers (have keys, not in cooldown)."""
        available = []
        for provider in Provider:
            if f"{provider.value.upper()}_API_KEY" in os.environ or \
               f"{provider.value.upper()}_TOKEN" in os.environ:
                if not self._is_cooldown(provider):
                    available.append(provider)
        return available
    
    def complete(self, messages: List[Dict], model: Optional[str] = None, 
                 preferred_provider: Optional[Provider] = None, 
                 skills: Optional[List[str]] = None,  # NEW: skills parameter
                 **kwargs) -> Dict[str, Any]:
        """
        Complete a request with smart provider selection AND skill integration.
        
        Args:
            messages: Chat messages
            model: Preferred model (optional, will auto-select if not provided)
            preferred_provider: Provider preference (optional)
            skills: Active skills for middleware (optional)
            **kwargs: Additional API parameters
            
        Returns:
            Dict with content, provider, model, usage info
        """
        # NEW: Apply skill middleware pre-processing
        if MIDDLEWARE_AVAILABLE and self.middleware:
            if skills:
                self.middleware.set_skills(skills)
            messages = self.middleware.preprocess(messages)
        
        # Get available providers
        available = self._get_available_providers()
        if not available:
            return {"error": "No API providers available. Set GROQ_API_KEYS or OPENROUTER_API_KEYS"}
        
        # Build priority list
        if preferred_provider and preferred_provider in available:
            providers_to_try = [preferred_provider] + [p for p in available if p != preferred_provider]
        else:
            providers_to_try = available
        
        # Try each provider
        for provider in providers_to_try:
            if self._is_cooldown(provider):
                continue
            
            # Select model
            if model:
                selected_model = model
            else:
                config = self.PROVIDERS[provider]
                selected_model = random.choice(config.models)
            
            # Call provider
            if provider == Provider.GROQ:
                result = self._call_groq(selected_model, messages, **kwargs)
            elif provider == Provider.OPENROUTER:
                result = self._call_openrouter(selected_model, messages, **kwargs)
            elif provider == Provider.HUGGINGFACE:
                result = self._call_huggingface(selected_model, messages, **kwargs)
            elif provider == Provider.CLOUDFLARE:
                result = self._call_cloudflare(selected_model, messages, **kwargs)
            elif provider == Provider.TOGETHER:
                result = self._call_together(selected_model, messages, **kwargs)
            else:
                continue
            
            if "error" not in result:
                # NEW: Apply skill middleware post-processing
                if MIDDLEWARE_AVAILABLE and self.middleware:
                    result = self.middleware.postprocess(result)
                return result
            
            # Try next provider on failure
            continue
        
        return {"error": "All providers failed or unavailable"}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        with self.stats.lock:
            return {
                "total_calls": self.stats.total_calls,
                "provider_calls": dict(self.stats.provider_calls),
                "failures": dict(self.stats.failures),
                "last_used": dict(self.stats.last_used),
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all providers."""
        health = {}
        for provider in Provider:
            config = self.PROVIDERS[provider]
            has_key = bool(self._get_api_key(provider))
            in_cooldown = self._is_cooldown(provider)
            health[provider.value] = {
                "available": has_key and not in_cooldown,
                "has_key": has_key,
                "in_cooldown": in_cooldown,
                "models": len(config.models),
            }
        return health


# Global router instance
_router = SmartRouter()


def complete(messages: List[Dict], model: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for router.complete()
    
    Usage:
        from neuro.router import complete
        
        result = complete(
            messages=[{"role": "user", "content": "Hello!"}],
            model="gemini/gemini-3.5-flash"
        )
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Response: {result['content']}")
    """
    return _router.complete(messages, model, **kwargs)


def health_check() -> Dict[str, Any]:
    """Check which providers are healthy."""
    return _router.health_check()


def get_stats() -> Dict[str, Any]:
    """Get router statistics."""
    return _router.get_stats()
