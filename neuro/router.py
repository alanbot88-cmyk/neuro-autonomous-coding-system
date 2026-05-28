"""
Neuro Router - Model routing with key pooling
Uses direct SDK calls - NO LiteLLM
"""

import os
import time
from typing import List, Optional

from neuro.models import APPROVED_MODELS, MODEL_ROLES


# =============================================================================
# KEY MANAGEMENT
# =============================================================================

def _get_env_keys(var_name: str) -> List[str]:
    """Get API keys from environment (supports comma-separated)."""
    value = os.getenv(var_name, "")
    if not value:
        return []
    return [k.strip() for k in value.split(",") if k.strip()]


# Load keys from environment
GEMINI_KEYS = _get_env_keys("GEMINI_API_KEYS")
GROQ_KEYS = _get_env_keys("GROQ_API_KEYS")
OPENROUTER_KEYS = _get_env_keys("OPENROUTER_API_KEYS")

# Fallback single key
if not GEMINI_KEYS:
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        GEMINI_KEYS = [key]

if not GROQ_KEYS:
    key = os.getenv("GROQ_API_KEY", "")
    if key:
        GROQ_KEYS = [key]

if not OPENROUTER_KEYS:
    key = os.getenv("OPENROUTER_API_KEY", "")
    if key:
        OPENROUTER_KEYS = [key]


# =============================================================================
# ROUTER
# =============================================================================

class NeuroRouter:
    """Neuro model router with key rotation."""
    
    def __init__(self):
        self.key_index = {"gemini": 0, "groq": 0, "openrouter": 0}
        self.cooldowns: dict[str, float] = {}
    
    def get_key(self, provider: str) -> Optional[str]:
        """Get next available key for provider."""
        if provider == "gemini":
            keys = GEMINI_KEYS
        elif provider == "groq":
            keys = GROQ_KEYS
        elif provider == "openrouter":
            keys = OPENROUTER_KEYS
        else:
            return None
        
        if not keys:
            return None
        
        # Round-robin with cooldowns
        for _ in range(len(keys)):
            idx = self.key_index[provider] % len(keys)
            self.key_index[provider] += 1
            key = keys[idx]
            
            # Check cooldown
            cooldown_key = f"{provider}:{idx}"
            if cooldown_key in self.cooldowns:
                if time.time() - self.cooldowns[cooldown_key] < 60:
                    continue
            
            return key
        
        return None
    
    def mark_rate_limited(self, provider: str, idx: int):
        """Mark a key as rate limited."""
        cooldown_key = f"{provider}:{idx}"
        self.cooldowns[cooldown_key] = time.time()


# Global router instance
_router = NeuroRouter()


# =============================================================================
# MODEL CALLS
# =============================================================================

def complete(role: str, messages: List[dict], model: Optional[str] = None, **kwargs) -> str:
    """
    Call a model through Neuro router.
    
    Args:
        role: Role (executor, planner, etc.) or model name
        messages: Chat messages
        model: Optional model override
    
    Returns:
        Model response string
    """
    # Determine model
    if model:
        provider, model_name = model.split("/", 1) if "/" in model else (model, model)
    elif role in MODEL_ROLES:
        model = MODEL_ROLES[role]["primary"]
        provider, model_name = model.split("/", 1)
    else:
        model = MODEL_ROLES["executor"]["primary"]
        provider, model_name = model.split("/", 1)
    
    # Get API key
    api_key = _router.get_key(provider)
    if not api_key:
        raise RuntimeError(f"No API key for {provider}")
    
    # Call provider
    try:
        if provider == "gemini":
            return _call_gemini(model_name, messages, api_key, **kwargs)
        elif provider == "groq":
            return _call_groq(model_name, messages, api_key, **kwargs)
        elif provider == "openrouter":
            return _call_openrouter(model_name, messages, api_key, **kwargs)
    except Exception as e:
        raise RuntimeError(f"Model call failed: {e}")


def _call_gemini(model: str, messages: list, api_key: str, **kwargs) -> str:
    """Call Gemini API."""
    try:
        import google.genai as genai
    except ImportError:
        raise RuntimeError("google-genai not installed: pip install google-genai")
    
    client = genai.Client(api_key=api_key)
    
    # Convert messages format
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(genai.Content(role=role, parts=[genai.Part(text=msg["content"])]))
    
    response = client.models.generate_content(
        model=model,
        contents=contents,
        **kwargs
    )
    
    return response.text


def _call_groq(model: str, messages: list, api_key: str, **kwargs) -> str:
    """Call Groq API."""
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("groq not installed: pip install groq")
    
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs
    )
    
    return response.choices[0].message.content


def _call_openrouter(model: str, messages: list, api_key: str, **kwargs) -> str:
    """Call OpenRouter API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai not installed: pip install openai")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs
    )
    
    return response.choices[0].message.content


# =============================================================================
# UTILITIES
# =============================================================================

def has_provider(provider: str) -> bool:
    """Check if provider has keys."""
    if provider == "gemini":
        return bool(GEMINI_KEYS)
    elif provider == "groq":
        return bool(GROQ_KEYS)
    elif provider == "openrouter":
        return bool(OPENROUTER_KEYS)
    return False


def available_providers() -> dict:
    """Get available providers and key counts."""
    return {
        "gemini": len(GEMINI_KEYS),
        "groq": len(GROQ_KEYS),
        "openrouter": len(OPENROUTER_KEYS),
    }