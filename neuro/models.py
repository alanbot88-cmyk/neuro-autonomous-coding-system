# Auto-generated - DO NOT EDIT
# Neuro Model Registry - 30 Models (Free Tier)
# Last saved: 2026-05-28

APPROVED_PROVIDERS = frozenset({'gemini', 'groq', 'openrouter'})

# All 30 approved models
APPROVED_MODELS = [
    # Gemini (4 models)
    "gemini/gemini-3.5-flash",
    "gemini/gemini-2.5-flash",
    "gemini/gemini-2.5-flash-lite",
    "gemini/gemini-3.1-flash-lite",
    
    # Groq (8 models)
    "groq/llama-3.3-70b-versatile",
    "groq/openai/gpt-oss-120b",
    "groq/openai/gpt-oss-20b",
    "groq/qwen/qwen3-32b",
    "groq/groq/compound",
    "groq/groq/compound-mini",
    "groq/llama-3.1-8b-instant",
    "groq/meta-llama/llama-4-scout-17b-16e-instruct",
    
    # OpenRouter (18 FREE models)
    "openrouter/qwen/qwen3-coder:free",
    "openrouter/qwen/qwen3-next-80b-a3b-instruct:free",
    "openrouter/google/gemma-4-31b-it:free",
    "openrouter/google/gemma-4-26b-a4b-it:free",
    "openrouter/deepseek/deepseek-v4-flash:free",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free",
    "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/openai/gpt-oss-120b:free",
    "openrouter/openai/gpt-oss-20b:free",
    "openrouter/liquid/lfm-2.5-1.2b-thinking:free",
    "openrouter/liquid/lfm-2.5-1.2b-instruct:free",
    "openrouter/poolside/laguna-xs.2:free",
    "openrouter/poolside/laguna-m.1:free",
    "openrouter/meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/nvidia/nemotron-nano-9b-v2:free",
    "openrouter/nvidia/nemotron-3-nano-30b-a3b:free",
    "openrouter/baidu/cobuddy:free",
    "openrouter/z-ai/glm-4.5-air:free",
]

# Model roles/configurations
MODEL_ROLES = {
    "executor": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/qwen/qwen3-coder:free"],
        "temperature": 0.1,
        "max_tokens": 8192,
    },
    "planner": {
        "primary": "gemini/gemini-3.5-flash",
        "fallback": ["gemini/gemini-2.5-flash", "openrouter/deepseek/deepseek-v4-flash:free"],
        "temperature": 0.2,
        "max_tokens": 8192,
    },
    "debugger": {
        "primary": "groq/llama-3.3-70b-versatile",
        "fallback": ["groq/qwen/qwen3-32b", "gemini/gemini-2.5-flash"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
    "reviewer": {
        "primary": "gemini/gemini-2.5-flash",
        "fallback": ["openrouter/meta-llama/llama-3.3-70b-instruct:free"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
}