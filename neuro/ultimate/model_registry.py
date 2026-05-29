"""
Neuro Ultimate - Complete Model Registry
==========================================
50+ FREE API models with task assignments and fallback chains.

Last Updated: 2026-05-29

API KEYS REQUIRED (set as environment variables):
- GEMINI_API_KEY: Google AI Studio free tier
- GROQ_API_KEY: Groq free tier (30 req/min)
- OPENROUTER_API_KEY: OpenRouter free credits
- TOGETHER_API_KEY: Together AI $5 free credits
- COHERE_API_KEY: Cohere trial
- HF_TOKEN: HuggingFace inference
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
# COMPLETE MODEL REGISTRY (50+ Models)
# =============================================================================

MODEL_REGISTRY: Dict[str, ModelInfo] = {
    
    # =========================================================================
    # GEMINI (Google AI Studio) - FREE TIER
    # =========================================================================
    
    "gemini-2.5-flash": ModelInfo(
        id="gemini-2.5-flash",
        provider=ModelProvider.GEMINI,
        name="Gemini 2.5 Flash",
        context_window=1_000_000,  # 1M tokens
        strengths=["fast_generation", "coding", "reasoning", "multimodal", "long_context"],
        rate_limits="15 req/min (free), 1500 req/day",
        cost="FREE (generous)",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-3.5-flash", "gemini-3-flash-preview"]
    ),
    
    "gemini-3.5-flash": ModelInfo(
        id="gemini-3.5-flash",
        provider=ModelProvider.GEMINI,
        name="Gemini 3.5 Flash",
        context_window=1_000_000,
        strengths=["advanced_reasoning", "coding", "analysis", "multimodal"],
        rate_limits="15 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-2.5-flash", "gemini-3-flash-preview"]
    ),
    
    "gemini-3-flash-preview": ModelInfo(
        id="gemini-3-flash-preview",
        provider=ModelProvider.GEMINI,
        name="Gemini 3 Flash Preview",
        context_window=1_000_000,
        strengths=["cutting_edge", "reasoning", "coding", "latest_features"],
        rate_limits="15 req/min (free)",
        cost="FREE",
        api_endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
        api_key_env="GEMINI_API_KEY",
        fallback_models=["gemini-2.5-flash", "gemini-3.5-flash"]
    ),
    
    # Additional Gemini models
    "gemini-1.5-pro": ModelInfo(
        id="gemini-1.5-pro",
        provider=ModelProvider.GEMINI,
        name="Gemini 1.5 Pro",
        context_window=2_000_000,  # 2M tokens
        strengths=["complex_reasoning", "long_context", "coding", "analysis"],
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
        fallback_models=["gemini-2.5-flash", "gemini-3.5-flash"]
    ),
    
    # =========================================================================
    # GROQ (Fast Inference) - FREE TIER
    # =========================================================================
    
    "groq-llama-3.3-70b-versatile": ModelInfo(
        id="llama-3.3-70b-versatile",
        provider=ModelProvider.GROQ,
        name="Llama 3.3 70B (Groq)",
        context_window=128_000,
        strengths=["fast_inference", "coding", "reasoning", "general_purpose"],
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
        strengths=["ultra_fast", "quick_responses", "efficient"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.3-70b-versatile"]
    ),
    
    "groq-qwen3-32b": ModelInfo(
        id="qwen3-32b",
        provider=ModelProvider.GROQ,
        name="Qwen3 32B (Groq)",
        context_window=128_000,
        strengths=["coding", "reasoning", "balanced"],
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
        strengths=["fast_moe", "coding", "reasoning"],
        rate_limits="30 req/min (free)",
        cost="FREE",
        api_endpoint="https://api.groq.com/openai/v1/chat/completions",
        api_key_env="GROQ_API_KEY",
        fallback_models=["groq-llama-3.3-70b-versatile"]
    ),
    
    # =========================================================================
    # OPENROUTER (18+ FREE Models)
    # =========================================================================
    
    # DeepSeek (BEST FOR CODING - 39.8% on SWE-bench!)
    "openrouter-deepseek-v4-flash": ModelInfo(
        id="deepseek/deepseek-v4-flash:free",
        provider=ModelProvider.OPENROUTER,
        name="DeepSeek V4 Flash (OpenRouter)",
        context_window=1_000_000,  # 1M tokens!
        strengths=["coding", "reasoning", "long_context", "agentic", "cost_effective"],
        rate_limits="Varies by model popularity",
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
        strengths=["coding", "reasoning", "general"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash", "openrouter-qwen3-coder"]
    ),
    
    # Qwen (MoE - 480B parameters!)
    "openrouter-qwen3-coder": ModelInfo(
        id="qwen/qwen3-coder:free",
        provider=ModelProvider.OPENROUTER,
        name="Qwen3 Coder (OpenRouter)",
        context_window=128_000,
        strengths=["coding", "MoE", "code_generation", "bug_detection"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash", "openrouter-llama-3.3-70b"]
    ),
    
    "openrouter-qwen3-80b": ModelInfo(
        id="qwen/qwen3-next-80b-a3b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Qwen3 80B A3B (OpenRouter)",
        context_window=128_000,
        strengths=["advanced_reasoning", "coding", "analysis"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash", "openrouter-qwen3-coder"]
    ),
    
    "openrouter-qwen2.5-72b": ModelInfo(
        id="qwen/qwen2.5-72b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Qwen 2.5 72B (OpenRouter)",
        context_window=128_000,
        strengths=["coding", "reasoning", "instruction_following"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-qwen3-coder", "openrouter-deepseek-v4-flash"]
    ),
    
    # Google Gemma
    "openrouter-gemma-4-31b": ModelInfo(
        id="google/gemma-4-31b-it:free",
        provider=ModelProvider.OPENROUTER,
        name="Gemma 4 31B (OpenRouter)",
        context_window=128_000,
        strengths=["efficient", "reasoning", "general"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash", "openrouter-llama-3.3-70b"]
    ),
    
    "openrouter-gemma-4-26b": ModelInfo(
        id="google/gemma-4-26b-a4b-it:free",
        provider=ModelProvider.OPENROUTER,
        name="Gemma 4 26B A4B (OpenRouter)",
        context_window=128_000,
        strengths=["efficient", "fast", "reasoning"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-gemma-4-31b", "openrouter-deepseek-v4-flash"]
    ),
    
    # Meta Llama
    "openrouter-llama-3.3-70b": ModelInfo(
        id="meta-llama/llama-3.3-70b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Llama 3.3 70B (OpenRouter)",
        context_window=128_000,
        strengths=["general", "reasoning", "coding", "open_source"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash", "openrouter-qwen3-coder"]
    ),
    
    "openrouter-llama-3.2-3b": ModelInfo(
        id="meta-llama/llama-3.2-3b-instruct:free",
        provider=ModelProvider.OPENROUTER,
        name="Llama 3.2 3B (OpenRouter)",
        context_window=128_000,
        strengths=["fast", "efficient", "quick_tasks"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b", "openrouter-deepseek-v4-flash"]
    ),
    
    # NVIDIA Nemotron
    "openrouter-nemotron-super-120b": ModelInfo(
        id="nvidia/nemotron-3-super-120b-a12b:free",
        provider=ModelProvider.OPENROUTER,
        name="Nemotron Super 120B (OpenRouter)",
        context_window=128_000,
        strengths=["large_model", "reasoning", "coding"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b", "openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-nemotron-nano-9b": ModelInfo(
        id="nvidia/nemotron-nano-9b-v2:free",
        provider=ModelProvider.OPENROUTER,
        name="Nemotron Nano 9B (OpenRouter)",
        context_window=128_000,
        strengths=["fast", "efficient", "nvidia_optimized"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b", "openrouter-gemma-4-31b"]
    ),
    
    "openrouter-nemotron-nano-30b": ModelInfo(
        id="nvidia/nemotron-3-nano-30b-a3b:free",
        provider=ModelProvider.OPENROUTER,
        name="Nemotron Nano 30B (OpenRouter)",
        context_window=128_000,
        strengths=["balanced", "reasoning", "coding"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-nemotron-super-120b", "openrouter-llama-3.3-70b"]
    ),
    
    # OpenAI OSS
    "openrouter-gpt-oss-120b": ModelInfo(
        id="openai/gpt-oss-120b:free",
        provider=ModelProvider.OPENROUTER,
        name="GPT OSS 120B (OpenRouter)",
        context_window=128_000,
        strengths=["large", "coding", "reasoning"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b", "openrouter-deepseek-v4-flash"]
    ),
    
    "openrouter-gpt-oss-20b": ModelInfo(
        id="openai/gpt-oss-20b:free",
        provider=ModelProvider.OPENROUTER,
        name="GPT OSS 20B (OpenRouter)",
        context_window=128_000,
        strengths=["fast", "efficient", "open_source"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-gpt-oss-120b", "openrouter-llama-3.2-3b"]
    ),
    
    # Liquid & Poolside
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
        strengths=["medium", "balanced", "poolside"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-llama-3.3-70b"]
    ),
    
    # Other OpenRouter models
    "openrouter-cobuddy": ModelInfo(
        id="baidu/cobuddy:free",
        provider=ModelProvider.OPENROUTER,
        name="CoBuddy (OpenRouter)",
        context_window=128_000,
        strengths=["baidu", "chinese", "reasoning"],
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
        strengths=["glm", "chinese", "efficient"],
        rate_limits="Varies",
        cost="FREE",
        api_endpoint="https://openrouter.ai/api/v1/chat/completions",
        api_key_env="OPENROUTER_API_KEY",
        fallback_models=["openrouter-deepseek-v4-flash", "openrouter-cobuddy"]
    ),
    
    # =========================================================================
    # TOGETHER AI (FREE CREDITS)
    # =========================================================================
    
    "together-llama-3.3-70b": ModelInfo(
        id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        provider=ModelProvider.TOGETHER,
        name="Llama 3.3 70B (Together)",
        context_window=128_000,
        strengths=["coding", "reasoning", "general"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-qwen-2.5-coder-32b", "together-mistral-7b"]
    ),
    
    "together-qwen-2.5-coder-32b": ModelInfo(
        id="Qwen/Qwen2.5-Coder-32B-Instruct",
        provider=ModelProvider.TOGETHER,
        name="Qwen 2.5 Coder 32B (Together)",
        context_window=128_000,
        strengths=["coding", "code_generation", "debugging"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-llama-3.3-70b", "together-deepseek-coder"]
    ),
    
    "together-mistral-7b": ModelInfo(
        id="mistralai/Mistral-7B-Instruct-v0.3",
        provider=ModelProvider.TOGETHER,
        name="Mistral 7B (Together)",
        context_window=128_000,
        strengths=["efficient", "reasoning", "fast"],
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
        strengths=["coding", "code_completion", "debugging"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-qwen-2.5-coder-32b", "together-llama-3.3-70b"]
    ),
    
    "together-codestral": ModelInfo(
        id="mistralai/Codestral-22B-v0.1",
        provider=ModelProvider.TOGETHER,
        name="Codestral 22B (Together)",
        context_window=128_000,
        strengths=["coding", "code_generation", "dedicated_coder"],
        rate_limits="$5 free credits",
        cost="FREE (credits)",
        api_endpoint="https://api.together.xyz/v1/chat/completions",
        api_key_env="TOGETHER_API_KEY",
        fallback_models=["together-qwen-2.5-coder-32b", "together-deepseek-coder"]
    ),
    
    # =========================================================================
    # COHERE (TRIAL CREDITS)
    # =========================================================================
    
    "cohere-command-r-plus": ModelInfo(
        id="command-r-plus",
        provider=ModelProvider.COHERE,
        name="Command R+ (Cohere)",
        context_window=128_000,
        strengths=["reasoning", "coding", "long_context", "tool_use"],
        rate_limits="Trial credits",
        cost="FREE (trial)",
        api_endpoint="https://api.cohere.ai/v1/chat",
        api_key_env="COHERE_API_KEY",
        fallback_models=["cohere-command-r", "openrouter-deepseek-v4-flash"]
    ),
    
    "cohere-command-r": ModelInfo(
        id="command-r",
        provider=ModelProvider.COHERE,
        name="Command R (Cohere)",
        context_window=128_000,
        strengths=["reasoning", "coding", "efficient"],
        rate_limits="Trial credits",
        cost="FREE (trial)",
        api_endpoint="https://api.cohere.ai/v1/chat",
        api_key_env="COHERE_API_KEY",
        fallback_models=["cohere-command-r-plus", "openrouter-deepseek-v4-flash"]
    ),
    
    # =========================================================================
    # HUGGINGFACE (FREE INFERENCE)
    # =========================================================================
    
    "huggingface-qwen-2.5-coder": ModelInfo(
        id="Qwen/Qwen2.5-Coder-32B-Instruct",
        provider=ModelProvider.HUGGINGFACE,
        name="Qwen 2.5 Coder (HuggingFace)",
        context_window=128_000,
        strengths=["coding", "code_generation"],
        rate_limits="Free inference tier",
        cost="FREE",
        api_endpoint="https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct",
        api_key_env="HF_TOKEN",
        fallback_models=["huggingface-deepseek-coder", "huggingface-starcoder2"]
    ),
    
    "huggingface-deepseek-coder": ModelInfo(
        id="deepseek-ai/DeepSeek-Coder-V2",
        provider=ModelProvider.HUGGINGFACE,
        name="DeepSeek Coder V2 (HuggingFace)",
        context_window=128_000,
        strengths=["coding", "code_completion"],
        rate_limits="Free inference tier",
        cost="FREE",
        api_endpoint="https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-Coder-V2",
        api_key_env="HF_TOKEN",
        fallback_models=["huggingface-qwen-2.5-coder", "huggingface-starcoder2"]
    ),
    
    "huggingface-starcoder2": ModelInfo(
        id="bigcode/starcoder2-15b",
        provider=ModelProvider.HUGGINGFACE,
        name="StarCoder2 15B (HuggingFace)",
        context_window=128_000,
        strengths=["code_completion", "open_source"],
        rate_limits="Free inference tier",
        cost="FREE",
        api_endpoint="https://api-inference.huggingface.co/models/bigcode/starcoder2-15b",
        api_key_env="HF_TOKEN",
        fallback_models=["huggingface-qwen-2.5-coder", "huggingface-deepseek-coder"]
    ),
    
    # =========================================================================
    # CLOUDFLARE WORKERS AI (FREE TIER)
    # =========================================================================
    
    "cloudflare-llama-3-70b": ModelInfo(
        id="@cf/meta/llama-3-70b-instruct",
        provider=ModelProvider.CLOUDFLARE,
        name="Llama 3 70B (Cloudflare)",
        context_window=128_000,
        strengths=["fast", "edge_computing", "free"],
        rate_limits="10K neurons/day",
        cost="FREE",
        api_endpoint="https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/meta/llama-3-70b-instruct",
        api_key_env="CLOUDFLARE_API_TOKEN",
        fallback_models=["cloudflare-mistral-7b", "openrouter-llama-3.3-70b"]
    ),
    
    "cloudflare-mistral-7b": ModelInfo(
        id="@cf/mistral/mistral-7b-instruct-v0.2",
        provider=ModelProvider.CLOUDFLARE,
        name="Mistral 7B (Cloudflare)",
        context_window=128_000,
        strengths=["fast", "edge", "efficient"],
        rate_limits="10K neurons/day",
        cost="FREE",
        api_endpoint="https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/mistral/mistral-7b-instruct-v0.2",
        api_key_env="CLOUDFLARE_API_TOKEN",
        fallback_models=["cloudflare-llama-3-70b"]
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
    # Code Generation
    TaskAssignment(
        task_type=TaskType.CODE_GENERATION,
        display_name="Code Generation",
        description="Generate new code, functions, classes",
        primary_model="openrouter-deepseek-v4-flash",
        secondary_model="together-qwen-2.5-coder-32b",
        tertiary_model="gemini-2.5-flash",
        why_primary="Best coding (39.8% on SWE-bench), 1M context",
        why_fallback="Specialized coder model with 32B params"
    ),
    
    # Deep Reasoning
    TaskAssignment(
        task_type=TaskType.DEEP_REASONING,
        display_name="Deep Reasoning",
        description="Complex reasoning, planning, analysis",
        primary_model="gemini-3.5-flash",
        secondary_model="openrouter-deepseek-v4-flash",
        tertiary_model="cohere-command-r-plus",
        why_primary="Advanced reasoning, 1M context, latest features",
        why_fallback="Agentic model with excellent reasoning"
    ),
    
    # Bug Detection
    TaskAssignment(
        task_type=TaskType.BUG_DETECTION,
        display_name="Bug Detection",
        description="Find and fix bugs, errors, issues",
        primary_model="openrouter-qwen3-coder",
        secondary_model="openrouter-deepseek-v4-flash",
        tertiary_model="gemini-2.5-flash",
        why_primary="MoE model (480B params), excellent at code analysis",
        why_fallback="Strong coding capability"
    ),
    
    # Code Review
    TaskAssignment(
        task_type=TaskType.CODE_REVIEW,
        display_name="Code Review",
        description="Review code, suggest improvements",
        primary_model="openrouter-llama-3.3-70b",
        secondary_model="openrouter-deepseek-v4-flash",
        tertiary_model="gemini-2.5-flash",
        why_primary="70B model with excellent review capability",
        why_fallback="Good coding + reasoning balance"
    ),
    
    # Test Writing
    TaskAssignment(
        task_type=TaskType.TEST_WRITING,
        display_name="Test Writing",
        description="Write unit tests, integration tests",
        primary_model="together-qwen-2.5-coder-32b",
        secondary_model="openrouter-qwen3-coder",
        tertiary_model="openrouter-deepseek-v4-flash",
        why_primary="Specialized coder model optimized for code",
        why_fallback="MoE model great at understanding code structure"
    ),
    
    # Fast Response
    TaskAssignment(
        task_type=TaskType.FAST_RESPONSE,
        display_name="Fast Response",
        description="Quick responses, simple queries",
        primary_model="groq-llama-3.1-8b-instant",
        secondary_model="openrouter-llama-3.2-3b",
        tertiary_model="cloudflare-mistral-7b",
        why_primary="Ultra-fast inference, optimized for speed",
        why_fallback="Small, fast models"
    ),
    
    # Long Context
    TaskAssignment(
        task_type=TaskType.LONG_CONTEXT,
        display_name="Long Context",
        description="Processing large files, repositories",
        primary_model="openrouter-deepseek-v4-flash",
        secondary_model="gemini-1.5-pro",
        tertiary_model="gemini-2.5-flash",
        why_primary="1M token context, excellent at long documents",
        why_fallback="2M token context available"
    ),
    
    # Agent Swarm
    TaskAssignment(
        task_type=TaskType.AGENT_SWARM,
        display_name="Agent Swarm",
        description="Parallel sub-agents, distributed tasks",
        primary_model="gemini-3.5-flash",
        secondary_model="groq-llama-3.3-70b-versatile",
        tertiary_model="openrouter-deepseek-v4-flash",
        why_primary="Fast, cheap, supports parallel execution",
        why_fallback="Fast inference for parallel agents"
    ),
    
    # Multimodal
    TaskAssignment(
        task_type=TaskType.MULTIMODAL,
        display_name="Multimodal",
        description="Image understanding, document processing",
        primary_model="gemini-2.5-flash",
        secondary_model="gemini-1.5-pro",
        tertiary_model="openrouter-deepseek-v4-flash",
        why_primary="Native multimodal, fast, reliable",
        why_fallback="2M context for documents"
    ),
    
    # Simple Task
    TaskAssignment(
        task_type=TaskType.SIMPLE_TASK,
        display_name="Simple Task",
        description="Simple queries, basic operations",
        primary_model="groq-llama-3.1-8b-instant",
        secondary_model="openrouter-llama-3.2-3b",
        tertiary_model="gemini-2.5-flash",
        why_primary="Fastest, cheapest option",
        why_fallback="Small efficient models"
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