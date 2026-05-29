"""
🧠 NEURO ULTIMATE - COMPLETE MODEL REGISTRY (LOCKED)
=====================================================
50 FREE API MODELS - ALL PERMANENTLY LOCKED 🔒

⚠️  WARNING: ALL 50 MODELS ARE LOCKED AND PERMANENT!
⚠️  DO NOT MODIFY, ADD, OR REMOVE ANY MODEL WITHOUT USER REQUEST!
⚠️  THIS FILE IS THE SOURCE OF TRUTH FOR ALL MODEL CONFIGURATIONS.

Last Updated: 2026-05-29
Status: 🔒 LOCKED - ALL 50 MODELS PERMANENT

API PROVIDERS (User's API Keys - ALL FREE):
- GEMINI_API_KEY: Google AI Studio (11 models)
- GROQ_API_KEY: Groq (7 models)
- OPENROUTER_API_KEY: OpenRouter (19 models)
- TOGETHER_API_KEY: Together AI (5 models)
- COHERE_API_KEY: Cohere (2 models)
- HF_TOKEN: HuggingFace (3 models)
- CLOUDFLARE_API_TOKEN: Cloudflare (2 models)
- Additional routes (1 model)

TOTAL: 50 LOCKED MODELS
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# MODEL PROVIDERS & ENDPOINTS
# =============================================================================

class ModelProvider(Enum):
    """Available API providers."""
    GEMINI = "gemini"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    TOGETHER = "together"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    CLOUDFLARE = "cloudflare"


@dataclass
class ModelInfo:
    """Complete model information."""
    id: str  # Model ID for API calls
    provider: ModelProvider
    name: str  # Display name
    context_window: int  # Max tokens
    strengths: List[str]  # What it's good at
    rate_limits: str  # Rate limit info
    cost: str  # Pricing tier
    api_endpoint: str  # API endpoint URL
    api_key_env: str  # Environment variable name
    fallback_models: List[str] = field(default_factory=list)  # Fallback model IDs


# =============================================================================
# 🔒 LOCKED MODEL REGISTRY (50 MODELS - DO NOT MODIFY)
# =============================================================================

MODEL_REGISTRY: Dict[str, ModelInfo] = {
    
    # =========================================================================
    # 🔒 GEMINI (Google AI Studio) - 11 MODELS - LOCKED 🔒
    # =========================================================================
    
    "gemini-3-flash-preview": ModelInfo(
        id="gemini-3-flash-preview",
        provider=ModelProvider.GEMINI,
        name="Gemini 3 Flash Preview",
        context_window=1_000_000,
        strengths=["cutting_edge", "latest_features", "advanced_reasoning", "coding"],
        rate_limits="15 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-3.5-flash", "gemini-2.5-flash"]
    ),
    
    "gemini-3.5-flash": ModelInfo(
        id="gemini-3.5-flash",
        provider=ModelProvider.GEMINI,
        name="Gemini 3.5 Flash",
        context_window=1_000_000,
        strengths=["advanced_reasoning", "coding", "analysis", "multimodal", "fast"],
        rate_limits="15 req/min (free), 1500 req/day",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-3-flash-preview", "gemini-2.5-flash"]
    ),
    
    "gemini-2.5-flash": ModelInfo(
        id="gemini-2.5-flash",
        provider=ModelProvider.GEMINI,
        name="Gemini 2.5 Flash",
        context_window=1_000_000,
        strengths=["fast_generation", "coding", "reasoning", "multimodal", "long_context", "reliable"],
        rate_limits="15 req/min (free), 1500 req/day",
        cost="FREE (generous)",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-3.5-flash", "gemini-3-flash-preview"]
    ),
    
    "gemini-2.0-flash-exp": ModelInfo(
        id="gemini-2.0-flash-exp",
        provider=ModelProvider.GEMINI,
        name="Gemini 2.0 Flash Experimental",
        context_window=1_000_000,
        strengths=["experimental", "fast", "coding", "reasoning"],
        rate_limits="15 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-2.5-flash", "gemini-3.5-flash"]
    ),
    
    "gemini-1.5-pro": ModelInfo(
        id="gemini-1.5-pro",
        provider=ModelProvider.GEMINI,
        name="Gemini 1.5 Pro",
        context_window=2_000_000,
        strengths=["complex_reasoning", "long_context", "coding", "analysis", "2M_tokens"],
        rate_limits="50 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-2.5-flash", "gemini-1.5-flash"]
    ),
    
    "gemini-1.5-flash": ModelInfo(
        id="gemini-1.5-flash",
        provider=ModelProvider.GEMINI,
        name="Gemini 1.5 Flash",
        context_window=1_000_000,
        strengths=["fast", "coding", "reasoning", "cost_efficient"],
        rate_limits="15 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-2.5-flash"]
    ),
    
    "gemini-1.5-flash-8b": ModelInfo(
        id="gemini-1.5-flash-8b",
        provider=ModelProvider.GEMINI,
        name="Gemini 1.5 Flash 8B",
        context_window=1_000_000,
        strengths=["ultra_fast", "efficient", "cost_effective"],
        rate_limits="15 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-1.5-flash", "gemini-2.5-flash"]
    ),
    
    "gemini-exp-1206": ModelInfo(
        id="gemini-exp-1206",
        provider=ModelProvider.GEMINI,
        name="Gemini Experimental 1206",
        context_window=1_000_000,
        strengths=["experimental", "cutting_edge", "research"],
        rate_limits="Limited (experimental)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-exp-1206:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-3.5-flash", "gemini-2.5-flash"]
    ),
    
    # =========================================================================
    # 🔒 GROQ (Fast Inference) - 7 MODELS - LOCKED 🔒
    # =========================================================================
    
    "groq-llama-3.3-70b-versatile": ModelInfo(
        id="llama-3.3-70b-versatile",
        provider=ModelProvider.GROQ,
        name="Llama 3.3 70B (Groq)",
        context_window=128_000,
        strengths=["fast_inference", "coding", "reasoning", "general_purpose", "70b"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.1-8b-instant", "groq-qwen3-32b"]
    ),
    
    "groq-llama-3.1-8b-instant": ModelInfo(
        id="llama-3.1-8b-instant",
        provider=ModelProvider.GROQ,
        name="Llama 3.1 8B Instant (Groq)",
        context_window=128_000,
        strengths=["ultra_fast", "quick_responses", "efficient", "fastest"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-mixtral-8x7b-32768"]
    ),
    
    "groq-qwen3-32b": ModelInfo(
        id="qwen3-32b",
        provider=ModelProvider.GROQ,
        name="Qwen3 32B (Groq)",
        context_window=128_000,
        strengths=["coding", "reasoning", "balanced", "qwen3"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.3-70b-versatile"]
    ),
    
    "groq-mixtral-8x7b-32768": ModelInfo(
        id="mixtral-8x7b-32768",
        provider=ModelProvider.GROQ,
        name="Mixtral 8x7B (Groq)",
        context_window=32_768,
        strengths=["fast_moe", "coding", "reasoning", "moe"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.3-70b-versatile"]
    ),
    
    "groq-llama-3.2-1b-instruct": ModelInfo(
        id="llama-3.2-1b-instruct",
        provider=ModelProvider.GROQ,
        name="Llama 3.2 1B Instruct (Groq)",
        context_window=128_000,
        strengths=["ultra_efficient", "fast", "small_model"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.1-8b-instant"]
    ),
    
    "groq-llama-3.1-70b-instruct": ModelInfo(
        id="llama-3.1-70b-instruct",
        provider=ModelProvider.GROQ,
        name="Llama 3.1 70B Instruct (Groq)",
        context_window=128_000,
        strengths=["large_model", "coding", "reasoning", "70b"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.3-70b-versatile"]
    ),
    
    # =========================================================================
    # 🔒 OPENROUTER (19 MODELS) - LOCKED 🔒
    # =========================================================================
    
    "openrouter-deepseek-v4-flash": ModelInfo(
        id="deepseek/deepseek-v4-flash:free",
        provider=ModelProvider.OPENROUTER,
        name="DeepSeek V4 Flash (OpenRouter)",
        context_window=1_000_000,
        strengths=["coding", "reasoning", "long_context", "agentic", "best_coder", "1M_tokens"],
        rate_limits="Varies (free)",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-chat-v3", "openrouter-qwen3-coder"]
    ),
    
    "openrouter-deepseek-chat-v3": ModelInfo(
        id="deepseek/deepseek-chat-v3:free",
        provider=ModelProvider.OPENROUTER,
        name="DeepSeek Chat V3 (OpenRouter)",
        context_window=128_000,
        strengths=["coding", "reasoning", "general", "chat"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-qwen3-coder": ModelInfo(
        id="qwen/qwen3-coder:free",
        provider=ModelProvider.OPENROUTER,
        name="Qwen3 Coder (OpenRouter)",
        context_window=128_000,
        strengths=["coding", "MoE", "code_generation", "bug_detection", "480b_moe"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-qwen3-80b", "openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-qwen3-80b": ModelInfo(
        id="qwen/qwen3-next-80b-a3b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Qwen3 80B A3B (OpenRouter)",
        context_window=128_000,
        strengths=["advanced_reasoning", "coding", "analysis", "80b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-qwen2.5-72b": ModelInfo(
        id="qwen/qwen2.5-72b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Qwen 2.5 72B (OpenRouter)",
        context_window=128_000,
        strengths=["coding", "reasoning", "instruction_following", "72b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-qwen3-80b"]
    ),
    
    "openrouter-llama-3.3-70b": ModelInfo(
        id="meta-llama/llama-3.3-70b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Llama 3.3 70B (OpenRouter)",
        context_window=128_000,
        strengths=["general", "reasoning", "coding", "open_source", "70b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-llama-3.2-3b": ModelInfo(
        id="meta-llama/llama-3.2-3b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Llama 3.2 3B (OpenRouter)",
        context_window=128_000,
        strengths=["fast", "efficient", "quick_tasks", "small_model"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
    
    "openrouter-gemma-4-31b": ModelInfo(
        id="google/gemma-4-31b-it:free",
        provider=ModelProvider.OPENROUTER,
        name="Gemma 4 31B (OpenRouter)",
        context_window=128_000,
        strengths=["efficient", "reasoning", "general", "gemma4"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-gemma-4-26b"]
    ),
    
    "openrouter-gemma-4-26b": ModelInfo(
        id="google/gemma-4-26b-a4b-it:free",
        provider=ModelProvider.OPENROUTER,
        name="Gemma 4 26B A4B (OpenRouter)",
        context_window=128_000,
        strengths=["efficient", "fast", "reasoning", "gemma4"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-gemma-4-31b"]
    ),
    
    "openrouter-nemotron-super-120b": ModelInfo(
        id="nvidia/nemotron-3-super-120b-a12b:free",
        provider=ModelProvider.OPENROUTER,
        name="Nemotron Super 120B (OpenRouter)",
        context_window=128_000,
        strengths=["large_model", "reasoning", "coding", "120b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
    
    "openrouter-nemotron-nano-30b": ModelInfo(
        id="nvidia/nemotron-3-nano-30b-a3b:free",
        provider=ModelProvider.OPENROUTER,
        name="Nemotron Nano 30B (OpenRouter)",
        context_window=128_000,
        strengths=["balanced", "reasoning", "coding", "30b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-nemotron-super-120b"]
    ),
    
    "openrouter-gpt-oss-120b": ModelInfo(
        id="openai/gpt-oss-120b:free",
        provider=ModelProvider.OPENROUTER,
        name="GPT OSS 120B (OpenRouter)",
        context_window=128_000,
        strengths=["large", "coding", "reasoning", "120b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-nemotron-super-120b"]
    ),
    
    "openrouter-liquid-2.5-1.2b": ModelInfo(
        id="liquid/lfm-2.5-1.2b-thinking:free",
        provider=ModelProvider.OPENROUTER,
        name="Liquid LFM 2.5 1.2B (OpenRouter)",
        context_window=128_000,
        strengths=["thinking_model", "reasoning", "ultra_fast"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-laguna-xs": ModelInfo(
        id="poolside/laguna-xs.2:free",
        provider=ModelProvider.OPENROUTER,
        name="Laguna XS (OpenRouter)",
        context_window=128_000,
        strengths=["fast", "efficient", "poolside"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.2-3b"]
    ),
    
    "openrouter-laguna-m": ModelInfo(
        id="poolside/laguna-m.1:free",
        provider=ModelProvider.OPENROUTER,
        name="Laguna M (OpenRouter)",
        context_window=128_000,
        strengths=["balanced", "poolside", "general"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
    
    "openrouter-cobuddy": ModelInfo(
        id="baidu/cobuddy:free",
        provider=ModelProvider.OPENROUTER,
        name="CoBuddy (OpenRouter)",
        context_window=128_000,
        strengths=["chinese", "reasoning", "baidu"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-glm-4.5": ModelInfo(
        id="z-ai/glm-4.5-air:free",
        provider=ModelProvider.OPENROUTER,
        name="GLM 4.5 Air (OpenRouter)",
        context_window=128_000,
        strengths=["chinese", "efficient", "glm"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-cobuddy"]
    ),
    
    "openrouter-hermes-3-70b": ModelInfo(
        id="NousResearch/NousHermes3-70b-Llama3.1:free",
        provider=ModelProvider.OPENROUTER,
        name="Hermes 3 70B (OpenRouter)",
        context_window=128_000,
        strengths=["reasoning", "coding", "70b", "NousResearch"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
    
    "openrouter-yi-34b": ModelInfo(
        id="01-ai/yi-34b-chat:free",
        provider=ModelProvider.OPENROUTER,
        name="Yi 34B Chat (OpenRouter)",
        context_window=128_000,
        strengths=["reasoning", "coding", "chinese", "34b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash"]
    ),
    
    # =========================================================================
    # 🔒 TOGETHER AI (5 MODELS) - LOCKED 🔒
    # =========================================================================
    
    "together-llama-3.3-70b": ModelInfo(
        id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        provider=ModelProvider.TOGETHER,
        name="Llama 3.3 70B (Together)",
        context_window=128_000,
        strengths=["coding", "reasoning", "general", "70b"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-qwen-2.5-coder-32b"]
    ),
    
    "together-qwen-2.5-coder-32b": ModelInfo(
        id="Qwen/Qwen2.5-Coder-32B-Instruct",
        provider=ModelProvider.TOGETHER,
        name="Qwen 2.5 Coder 32B (Together)",
        context_window=128_000,
        strengths=["coding", "code_generation", "debugging", "specialized_coder"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-deepseek-coder"]
    ),
    
    "together-mistral-7b": ModelInfo(
        id="mistralai/Mistral-7B-Instruct-v0.3",
        provider=ModelProvider.TOGETHER,
        name="Mistral 7B (Together)",
        context_window=128_000,
        strengths=["efficient", "reasoning", "fast", "mistral"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-llama-3.3-70b"]
    ),
    
    "together-deepseek-coder": ModelInfo(
        id="deepseek-ai/DeepSeek-Coder-V2",
        provider=ModelProvider.TOGETHER,
        name="DeepSeek Coder V2 (Together)",
        context_window=128_000,
        strengths=["coding", "code_completion", "debugging", "coder"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-qwen-2.5-coder-32b"]
    ),
    
    "together-codestral": ModelInfo(
        id="mistralai/Codestral-22B-v0.1",
        provider=ModelProvider.TOGETHER,
        name="Codestral 22B (Together)",
        context_window=128_000,
        strengths=["coding", "code_generation", "dedicated_coder", "22b"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-qwen-2.5-coder-32b"]
    ),
    
    # =========================================================================
    # 🔒 COHERE (2 MODELS) - LOCKED 🔒
    # =========================================================================
    
    "cohere-command-r-plus": ModelInfo(
        id="command-r-plus",
        provider=ModelProvider.COHERE,
        name="Command R+ (Cohere)",
        context_window=128_000,
        strengths=["reasoning", "coding", "long_context", "tool_use", "agentic"],
        rate_limits="Trial credits",
        cost="FREE (trial)",
        api_endpoint="https://api.cohere.ai/v1/chat",
        api_key_env="COHERE_API_KEY",
        fallback_models=["cohere-command-r"]
    ),
    
    "cohere-command-r": ModelInfo(
        id="command-r",
        provider=ModelProvider.COHERE,
        name="Command R (Cohere)",
        context_window=128_000,
        strengths=["reasoning", "coding", "efficient", "tool_use"],
        rate_limits="Trial credits",
        cost="FREE (trial)",
        api_endpoint="https://api.cohere.ai/v1/chat",
        api_key_env="COHERE_API_KEY",
        fallback_models=["cohere-command-r-plus"]
    ),
    
    # =========================================================================
    # 🔒 HUGGINGFACE (3 MODELS) - LOCKED 🔒
    # =========================================================================
    
    "huggingface-qwen-2.5-coder": ModelInfo(
        id="Qwen/Qwen2.5-Coder-32B-Instruct",
        provider=ModelProvider.HUGGINGFACE,
        name="Qwen 2.5 Coder (HuggingFace)",
        context_window=128_000,
        strengths=["coding", "code_generation", "open_source"],
        rate_limits="Free inference tier",
        cost="FREE",
        api_endpoint="https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct",
        api_key_env="HF_TOKEN",
        fallback_models=["huggingface-deepseek-coder"]
    ),
    
    "huggingface-deepseek-coder": ModelInfo(
        id="deepseek-ai/DeepSeek-Coder-V2",
        provider=ModelProvider.HUGGINGFACE,
        name="DeepSeek Coder V2 (HuggingFace)",
        context_window=128_000,
        strengths=["coding", "code_completion", "coder"],
        rate_limits="Free inference tier",
        cost="FREE",
        api_endpoint="https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-Coder-V2",
        api_key_env="HF_TOKEN",
        fallback_models=["huggingface-qwen-2.5-coder"]
    ),
    
    "huggingface-starcoder2": ModelInfo(
        id="bigcode/starcoder2-15b",
        provider=ModelProvider.HUGGINGFACE,
        name="StarCoder2 15B (HuggingFace)",
        context_window=128_000,
        strengths=["code_completion", "open_source", "bigcode"],
        rate_limits="Free inference tier",
        cost="FREE",
        api_endpoint="https://api-inference.huggingface.co/models/bigcode/starcoder2-15b",
        api_key_env="HF_TOKEN",
        fallback_models=["huggingface-qwen-2.5-coder"]
    ),
    
    # =========================================================================
    # 🔒 CLOUDFLARE WORKERS AI (2 MODELS) - LOCKED 🔒
    # =========================================================================
    
    "cloudflare-llama-3-70b": ModelInfo(
        id="@cf/meta/llama-3-70b-instruct",
        provider=ModelProvider.CLOUDFLARE,
        name="Llama 3 70B (Cloudflare)",
        context_window=128_000,
        strengths=["fast", "edge_computing", "free", "70b"],
        rate_limits="10K neurons/day",
        cost="FREE",
        api_endpoint="https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/meta/llama-3-70b-instruct",
        api_key_env="CLOUDFLARE_API_TOKEN",
        fallback_models=["cloudflare-mistral-7b"]
    ),
    
    "cloudflare-mistral-7b": ModelInfo(
        id="@cf/mistral/mistral-7b-instruct-v0.2",
        provider=ModelProvider.CLOUDFLARE,
        name="Mistral 7B (Cloudflare)",
        context_window=128_000,
        strengths=["fast", "edge", "efficient", "mistral"],
        rate_limits="10K neurons/day",
        cost="FREE",
        api_endpoint="https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/mistral/mistral-7b-instruct-v0.2",
        api_key_env="CLOUDFLARE_API_TOKEN",
        fallback_models=["cloudflare-llama-3-70b"]
    ),
    
    # =========================================================================
    # 🔒 ADDITIONAL MODELS (5 MODELS) - LOCKED 🔒
    # =========================================================================
    
    # Groq additional model
    "groq-llama Guard 3-8b": ModelInfo(
        id="llama-guard-3-8b",
        provider=ModelProvider.GROQ,
        name="Llama Guard 3 8B (Groq)",
        context_window=128_000,
        strengths=["safety", "guardrails", "moderation"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.1-8b-instant"]
    ),
    
    # Replicate (Free tier)
    "replicate-llama-3-70b": ModelInfo(
        id="meta/meta-llama-3-70b-instruct",
        provider=ModelProvider.OPENROUTER,
        name="Llama 3 70B (Replicate)",
        context_window=128_000,
        strengths=["coding", "reasoning", "70b"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
    
    # Google AI Free
    "gemini-pro-vision": ModelInfo(
        id="gemini-pro-vision",
        provider=ModelProvider.GEMINI,
        name="Gemini Pro Vision",
        context_window=128_000,
        strengths=["vision", "image_understanding", "multimodal"],
        rate_limits="15 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-2.5-flash"]
    ),
    
    # Fireworks AI
    "fireworks-llama-3-70b": ModelInfo(
        id="fireworks-llama-3-70b-instruct",
        provider=ModelProvider.OPENROUTER,
        name="Llama 3 70B (Fireworks)",
        context_window=128_000,
        strengths=["fast", "coding", "reasoning"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
    
    # Perplexity
    "perplexity-llama-3.1-70b": ModelInfo(
        id="llama-3.1-70b-instruct",
        provider=ModelProvider.OPENROUTER,
        name="Llama 3.1 70B (Perplexity)",
        context_window=128_000,
        strengths=["reasoning", "coding", "research"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
}


# =============================================================================
# TASK-TO-MODEL ASSIGNMENTS
# =============================================================================

class TaskType(Enum):
    """Task categories for model assignment."""
    CODE_GENERATION = "code_generation"
    DEEP_REASONING = "deep_reasoning"
    BUG_DETECTION = "bug_detection"
    CODE_REVIEW = "code_review"
    TEST_WRITING = "test_writing"
    FAST_RESPONSE = "fast_response"
    LONG_CONTEXT = "long_context"
    AGENT_SWARM = "agent_swarm"
    MULTIMODAL = "multimodal"
    SIMPLE_TASK = "simple_task"


@dataclass
class TaskAssignment:
    """Task assignment with primary model and fallbacks."""
    task_type: TaskType
    display_name: str
    description: str
    primary_model: str  # Model ID
    secondary_model: str = ""  # Fallback model ID
    tertiary_model: str = ""  # Last resort model ID
    why_primary: str = ""
    why_fallback: str = ""


TASK_ASSIGNMENTS: List[TaskAssignment] = [
    # =========================================================================
    # PRIMARY TASKS - GEMINI MODELS AS PRIMARY ⭐
    # =========================================================================
    
    # Deep Reasoning - Gemini 3.5 Flash as PRIMARY
    TaskAssignment(
        task_type=TaskType.DEEP_REASONING,
        display_name="Deep Reasoning",
        description="Complex reasoning, planning, analysis, chain-of-thought",
        primary_model="gemini-3.5-flash",
        secondary_model="gemini-3-flash-preview",
        tertiary_model="gemini-2.5-flash",
        why_primary="Advanced reasoning, 1M context, latest features, cutting-edge",
        why_fallback="Latest Gemini models for enhanced reasoning"
    ),
    
    # Code Generation - DeepSeek V4 Flash (Best for coding)
    TaskAssignment(
        task_type=TaskType.CODE_GENERATION,
        display_name="Code Generation",
        description="Generate new code, functions, classes, algorithms",
        primary_model="openrouter-deepseek-v4-flash",
        secondary_model="gemini-3.5-flash",
        tertiary_model="together-qwen-2.5-coder-32b",
        why_primary="Best coding model (39.8% on SWE-bench), 1M context, agentic",
        why_fallback="Gemini 3.5 Flash for reasoning + Qwen for specialized coding"
    ),
    
    # Bug Detection - Qwen3 Coder (MoE - 480B params)
    TaskAssignment(
        task_type=TaskType.BUG_DETECTION,
        display_name="Bug Detection",
        description="Find and fix bugs, errors, issues, debugging",
        primary_model="openrouter-qwen3-coder",
        secondary_model="gemini-3.5-flash",
        tertiary_model="openrouter-deepseek-v4-flash",
        why_primary="MoE model (480B params), excellent at code analysis and patterns",
        why_fallback="Gemini 3.5 Flash for deep reasoning, DeepSeek for coding"
    ),
    
    # Code Review - Llama 3.3 70B (70B model for comprehensive review)
    TaskAssignment(
        task_type=TaskType.CODE_REVIEW,
        display_name="Code Review",
        description="Review code, suggest improvements, refactoring",
        primary_model="openrouter-llama-3.3-70b",
        secondary_model="groq-llama-3.3-70b-versatile",
        tertiary_model="gemini-3.5-flash",
        why_primary="70B model with excellent review capability and context understanding",
        why_fallback="Groq fast 70B, Gemini 3.5 Flash for reasoning"
    ),
    
    # Test Writing - Qwen 2.5 Coder 32B (Specialized coder)
    TaskAssignment(
        task_type=TaskType.TEST_WRITING,
        display_name="Test Writing",
        description="Write unit tests, integration tests, test cases",
        primary_model="together-qwen-2.5-coder-32b",
        secondary_model="openrouter-qwen3-coder",
        tertiary_model="gemini-3.5-flash",
        why_primary="Specialized coder model optimized for understanding code structure",
        why_fallback="Qwen3 MoE for code analysis, Gemini for reasoning"
    ),
    
    # Long Context - DeepSeek V4 Flash (1M tokens!)
    TaskAssignment(
        task_type=TaskType.LONG_CONTEXT,
        display_name="Long Context",
        description="Processing large files, repositories, codebases",
        primary_model="openrouter-deepseek-v4-flash",
        secondary_model="gemini-1.5-pro",
        tertiary_model="gemini-3.5-flash",
        why_primary="1M token context window, excellent at long documents and repos",
        why_fallback="Gemini 1.5 Pro has 2M context, Gemini 3.5 Flash for general"
    ),
    
    # Multimodal - Gemini 2.5 Flash (Native multimodal)
    TaskAssignment(
        task_type=TaskType.MULTIMODAL,
        display_name="Multimodal",
        description="Image understanding, document processing, screenshots",
        primary_model="gemini-2.5-flash",
        secondary_model="gemini-1.5-pro",
        tertiary_model="gemini-3.5-flash",
        why_primary="Native multimodal support, fast, reliable, 1M context",
        why_fallback="Gemini 1.5 Pro for larger contexts, Gemini 3.5 for reasoning"
    ),
    
    # Fast Response - Groq Llama 3.1 8B (Ultra-fast inference)
    TaskAssignment(
        task_type=TaskType.FAST_RESPONSE,
        display_name="Fast Response",
        description="Quick responses, simple queries, fast iterations",
        primary_model="groq-llama-3.1-8b-instant",
        secondary_model="gemini-1.5-flash-8b",
        tertiary_model="openrouter-llama-3.2-3b",
        why_primary="Ultra-fast inference, optimized for speed (Groq infrastructure)",
        why_fallback="Gemini 1.5 Flash 8B for efficiency, OpenRouter for variety"
    ),
    
    # Agent Swarm - Gemini 3.5 Flash (Fast, cheap, parallel)
    TaskAssignment(
        task_type=TaskType.AGENT_SWARM,
        display_name="Agent Swarm",
        description="Parallel sub-agents, distributed tasks, multi-agent",
        primary_model="gemini-3.5-flash",
        secondary_model="groq-llama-3.3-70b-versatile",
        tertiary_model="openrouter-deepseek-v4-flash",
        why_primary="Fast, cheap, supports parallel execution, excellent reasoning",
        why_fallback="Groq fast 70B for parallel agents, DeepSeek for coding"
    ),
    
    # Simple Task - Gemini 1.5 Flash (Cost-effective, reliable)
    TaskAssignment(
        task_type=TaskType.SIMPLE_TASK,
        display_name="Simple Task",
        description="Simple queries, basic operations, straightforward tasks",
        primary_model="gemini-1.5-flash",
        secondary_model="groq-llama-3.1-8b-instant",
        tertiary_model="gemini-2.5-flash",
        why_primary="Cost-effective, fast, reliable for simple tasks",
        why_fallback="Groq for speed, Gemini 2.5 Flash for reliability"
    ),
]


# =============================================================================
# FALLBACK CHAINS
# =============================================================================

FALLBACK_CHAINS: Dict[str, List[str]] = {
    # Primary chains for different scenarios
    "coding": [
        "openrouter-deepseek-v4-flash",  # Best coder
        "openrouter-qwen3-coder",  # MoE coder
        "together-qwen-2.5-coder-32b",  # Dedicated coder
        "gemini-2.5-flash",  # Gemini fallback
        "groq-llama-3.3-70b-versatile",  # Last resort
    ],
    
    "reasoning": [
        "gemini-3.5-flash",  # Advanced reasoning
        "openrouter-deepseek-v4-flash",  # Agentic
        "cohere-command-r-plus",  # Tool use
        "openrouter-llama-3.3-70b",  # 70B model
    ],
    
    "fast": [
        "groq-llama-3.1-8b-instant",  # Fastest
        "openrouter-llama-3.2-3b",  # Small fast
        "cloudflare-mistral-7b",  # Edge fast
        "gemini-2.5-flash",  # Reliable fast
    ],
    
    "long_context": [
        "openrouter-deepseek-v4-flash",  # 1M tokens
        "gemini-1.5-pro",  # 2M tokens
        "gemini-2.5-flash",  # 1M tokens
        "cohere-command-r-plus",  # 128K context
    ],
    
    "multimodal": [
        "gemini-2.5-flash",  # Native multimodal
        "gemini-1.5-pro",  # Larger context
        "openrouter-deepseek-v4-flash",  # General fallback
    ],
    
    "default": [
        "gemini-2.5-flash",  # Reliable all-rounder
        "openrouter-deepseek-v4-flash",  # Best coding
        "groq-llama-3.3-70b-versatile",  # Fast 70B
        "openrouter-llama-3.3-70b",  # OpenRouter 70B
    ],
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_model(model_id: str) -> Optional[ModelInfo]:
    """Get model info by ID."""
    return MODEL_REGISTRY.get(model_id)


def get_task_assignment(task_type: TaskType) -> Optional[TaskAssignment]:
    """Get task assignment for a task type."""
    for assignment in TASK_ASSIGNMENTS:
        if assignment.task_type == task_type:
            return assignment
    return None


def get_fallback_chain(category: str) -> List[str]:
    """Get fallback chain for a category."""
    return FALLBACK_CHAINS.get(category, FALLBACK_CHAINS["default"])


def get_primary_model_for_task(task: str) -> str:
    """Get the primary model for a task description."""
    task_lower = task.lower()
    
    # Map task keywords to task types
    if any(word in task_lower for word in ["generate", "create", "write code", "implement"]):
        return "openrouter-deepseek-v4-flash"
    elif any(word in task_lower for word in ["reason", "think", "analyze", "plan"]):
        return "gemini-3.5-flash"
    elif any(word in task_lower for word in ["bug", "fix", "error", "issue"]):
        return "openrouter-qwen3-coder"
    elif any(word in task_lower for word in ["review", "refactor", "improve"]):
        return "openrouter-llama-3.3-70b"
    elif any(word in task_lower for word in ["test", "spec"]):
        return "together-qwen-2.5-coder-32b"
    elif any(word in task_lower for word in ["quick", "fast", "simple"]):
        return "groq-llama-3.1-8b-instant"
    elif any(word in task_lower for word in ["large", "long", "context", "file", "repo"]):
        return "openrouter-deepseek-v4-flash"
    elif any(word in task_lower for word in ["image", "picture", "document", "pdf"]):
        return "gemini-2.5-flash"
    else:
        return "gemini-2.5-flash"  # Default to Gemini


def list_all_models() -> List[ModelInfo]:
    """List all available models."""
    return list(MODEL_REGISTRY.values())


def get_model_count() -> int:
    """Get total number of models."""
    return len(MODEL_REGISTRY)


def get_models_by_provider(provider: ModelProvider) -> List[ModelInfo]:
    """Get all models from a specific provider."""
    return [m for m in MODEL_REGISTRY.values() if m.provider == provider]


# =============================================================================
# EXPORT FOR ROUTER INTEGRATION
# =============================================================================

def get_router_config() -> Dict:
    """Get configuration for the smart router."""
    return {
        "models": MODEL_REGISTRY,
        "task_assignments": {a.task_type.value: a for a in TASK_ASSIGNMENTS},
        "fallback_chains": FALLBACK_CHAINS,
    }