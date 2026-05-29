# Neuro Model Registry - 50+ Models (Free Tier)
# Task-to-Model Assignment with 20+ Categories
# Last saved: 2026-05-29

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ModelRole(Enum):
    """Model roles for task routing."""
    PLANNER = "planner"      # Task decomposition, planning
    ARCHITECT = "architect"  # System design, architecture
    CODER = "coder"         # Code implementation
    DEBUGGER = "debugger"   # Error analysis and fixing
    VALIDATOR = "validator" # Test validation, checking
    REFACTOR = "refactor"    # Code cleanup, refactoring
    REVIEWER = "reviewer"    # Code review, security audit
    FRONTEND = "frontend"    # UI/UX, frontend tasks
    DOCUMENTATION = "doc"    # Documentation generation


@dataclass
class ModelMetadata:
    """Structured metadata for a model."""
    name: str
    provider: str
    roles: List[str]
    strengths: List[str]
    priority: int  # 1 = highest
    fallback_priority: int
    cost: str  # "free", "cheap", "expensive"
    requires_key: bool
    context_window: Optional[int]
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "provider": self.provider,
            "roles": self.roles,
            "strengths": self.strengths,
            "priority": self.priority,
            "fallback_priority": self.fallback_priority,
            "cost": self.cost,
            "requires_key": self.requires_key,
            "context_window": self.context_window,
            "enabled": self.enabled,
        }


APPROVED_PROVIDERS = frozenset({
    'gemini', 'groq', 'openrouter', 'together', 'huggingface', 
    'cloudflare', 'cohere', 'lepton', 'mistral', 'perplexity'
})

# All 50+ models with structured metadata
MODEL_REGISTRY: List[ModelMetadata] = [
    # =============================================================================
    # GEMINI MODELS (5 models)
    # =============================================================================
    ModelMetadata(
        name="gemini/gemini-3.5-flash",
        provider="gemini",
        roles=["planner", "architect", "coder", "validator"],
        strengths=["fast", "reasoning", "long-context", "code"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-2.5-flash",
        provider="gemini",
        roles=["planner", "coder", "debugger"],
        strengths=["fast", "code", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-2.5-flash-lite",
        provider="gemini",
        roles=["coder", "frontend"],
        strengths=["fast", "cheap"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-3.1-flash-lite",
        provider="gemini",
        roles=["coder"],
        strengths=["fast", "cheap"],
        priority=4,
        fallback_priority=5,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    ModelMetadata(
        name="gemini/gemini-2.0-flash-exp",
        provider="gemini",
        roles=["planner", "architect", "debugger"],
        strengths=["reasoning", "long-context"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=1000000,
    ),
    
    # =============================================================================
    # GROQ MODELS (6 models)
    # =============================================================================
    ModelMetadata(
        name="groq/llama-3.3-70b-versatile",
        provider="groq",
        roles=["planner", "architect", "coder", "debugger", "refactor"],
        strengths=["fast", "reasoning", "code", "long-context"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="groq/llama-3.1-8b-instant",
        provider="groq",
        roles=["coder", "frontend", "documentation"],
        strengths=["fast", "cheap"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="groq/qwen/qwen3-32b",
        provider="groq",
        roles=["coder", "debugger", "planner"],
        strengths=["code", "reasoning", "fast"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="groq/llama-4-scout-17b-16e-instruct",
        provider="groq",
        roles=["coder", "frontend"],
        strengths=["code", "fast"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=100000,
    ),
    ModelMetadata(
        name="groq/llama-3.2-90b-vision-instruct",
        provider="groq",
        roles=["frontend", "architect", "reviewer"],
        strengths=["vision", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="groq/mixtral-8x7b-32768",
        provider="groq",
        roles=["planner", "architect"],
        strengths=["reasoning", "long-context"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32768,
    ),
    
    # =============================================================================
    # OPENROUTER FREE MODELS (20+ models)
    # =============================================================================
    ModelMetadata(
        name="openrouter/deepseek/deepseek-v4-flash:free",
        provider="openrouter",
        roles=["planner", "architect", "debugger", "validator"],
        strengths=["reasoning", "long-context", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=64000,
    ),
    ModelMetadata(
        name="openrouter/qwen/qwen3-coder:free",
        provider="openrouter",
        roles=["coder", "debugger", "validator"],
        strengths=["code", "fast", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/qwen/qwen3-next-80b-a3b-instruct:free",
        provider="openrouter",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/google/gemma-4-31b-it:free",
        provider="openrouter",
        roles=["frontend", "architect", "refactor"],
        strengths=["reasoning", "frontend", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/google/gemma-4-26b-a4b-it:free",
        provider="openrouter",
        roles=["frontend", "coder"],
        strengths=["frontend", "fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/meta-llama/llama-3.3-70b-instruct:free",
        provider="openrouter",
        roles=["planner", "architect", "reviewer"],
        strengths=["reasoning", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="openrouter/meta-llama/llama-3.2-3b-instruct:free",
        provider="openrouter",
        roles=["documentation", "frontend"],
        strengths=["fast", "cheap", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        provider="openrouter",
        roles=["architect", "reviewer", "security"],
        strengths=["reasoning", "code", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/openai/gpt-oss-120b:free",
        provider="openrouter",
        roles=["planner", "architect"],
        strengths=["reasoning", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/openai/gpt-oss-20b:free",
        provider="openrouter",
        roles=["coder", "frontend"],
        strengths=["fast", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/liquid/lfm-2.5-1.2b-thinking:free",
        provider="openrouter",
        roles=["planner", "debugger"],
        strengths=["reasoning", "fast", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/poolside/laguna-m.1:free",
        provider="openrouter",
        roles=["coder"],
        strengths=["code", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/baidu/cobuddy:free",
        provider="openrouter",
        roles=["frontend", "documentation"],
        strengths=["frontend", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/z-ai/glm-4.5-air:free",
        provider="openrouter",
        roles=["coder", "planner"],
        strengths=["fast", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/inflection/inflection-3-pi:free",
        provider="openrouter",
        roles=["planner", "architect"],
        strengths=["reasoning", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/mistralai/mistral-nemo:free",
        provider="openrouter",
        roles=["coder", "frontend"],
        strengths=["code", "fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/anthropic/claude-3-haiku:free",
        provider="openrouter",
        roles=["debugger", "validator"],
        strengths=["fast", "reasoning", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=200000,
    ),
    ModelMetadata(
        name="openrouter/microsoft/phi-4:free",
        provider="openrouter",
        roles=["coder", "debugger"],
        strengths=["code", "fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=16000,
    ),
    ModelMetadata(
        name="openrouter/minimax/minimax-m2.5:free",
        provider="openrouter",
        roles=["documentation", "frontend"],
        strengths=["fast", "free"],
        priority=3,
        fallback_priority=4,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    # Qwen via OpenRouter (user specified Qwen/DeepSeek use OpenRouter)
    ModelMetadata(
        name="openrouter/qwen/qwen3-32b",
        provider="openrouter",
        roles=["coder", "planner", "debugger"],
        strengths=["code", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="openrouter/qwen/qwen2.5-72b-instruct",
        provider="openrouter",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    # DeepSeek via OpenRouter
    ModelMetadata(
        name="openrouter/deepseek/deepseek-coder-v2",
        provider="openrouter",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=64000,
    ),
    ModelMetadata(
        name="openrouter/deepseek/deepseek-chat",
        provider="openrouter",
        roles=["planner", "debugger"],
        strengths=["reasoning"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=64000,
    ),
    
    # =============================================================================
    # TOGETHER AI MODELS (5 models)
    # =============================================================================
    ModelMetadata(
        name="together/llama-3.3-70b-instruct",
        provider="together",
        roles=["planner", "architect", "reviewer"],
        strengths=["reasoning", "code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="together/qwen-2.5-72b-instruct",
        provider="together",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="together/qwen-2.5-coder-32b-instruct",
        provider="together",
        roles=["coder", "debugger"],
        strengths=["code", "fast"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="together/mixtral-8x7b-instruct",
        provider="together",
        roles=["coder", "planner"],
        strengths=["code"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="together/deepseek-coder-v2-instruct",
        provider="together",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=64000,
    ),
    
    # =============================================================================
    # HUGGINGFACE MODELS (5 models)
    # =============================================================================
    ModelMetadata(
        name="huggingface/Qwen2.5-Coder-32B-Instruct",
        provider="huggingface",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="huggingface/DeepSeek-Coder-V2",
        provider="huggingface",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=64000,
    ),
    ModelMetadata(
        name="huggingface/CodeLlama-70B-Instruct",
        provider="huggingface",
        roles=["coder", "reviewer"],
        strengths=["code", "reasoning"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=16000,
    ),
    ModelMetadata(
        name="huggingface/Starcoder2-15B",
        provider="huggingface",
        roles=["coder"],
        strengths=["code"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=14000,
    ),
    ModelMetadata(
        name="huggingface/WizardCoder-33B",
        provider="huggingface",
        roles=["coder", "debugger"],
        strengths=["code"],
        priority=1,
        fallback_priority=2,
        cost="cheap",
        requires_key=True,
        context_window=18000,
    ),
    
    # =============================================================================
    # CLOUDFLARE MODELS (3 models)
    # =============================================================================
    ModelMetadata(
        name="cloudflare/@cf/meta/llama-3.1-70b-instruct",
        provider="cloudflare",
        roles=["planner", "architect", "coder"],
        strengths=["fast", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="cloudflare/@cf/mistral/mistral-7b-instruct-v0.2",
        provider="cloudflare",
        roles=["coder", "frontend"],
        strengths=["fast", "free"],
        priority=2,
        fallback_priority=3,
        cost="free",
        requires_key=True,
        context_window=32000,
    ),
    ModelMetadata(
        name="cloudflare/@cf/deepseek-ai/deepseek-coder-6.7b",
        provider="cloudflare",
        roles=["coder", "debugger"],
        strengths=["code", "fast", "free"],
        priority=1,
        fallback_priority=2,
        cost="free",
        requires_key=True,
        context_window=16000,
    ),
    
    # =============================================================================
    # ADDITIONAL PROVIDERS
    # =============================================================================
    # Cohere (3 models)
    ModelMetadata(
        name="cohere/command-r-plus",
        provider="cohere",
        roles=["planner", "architect"],
        strengths=["reasoning"],
        priority=2,
        fallback_priority=3,
        cost="expensive",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="cohere/command-r",
        provider="cohere",
        roles=["planner", "coder"],
        strengths=["reasoning", "code"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="cohere/command",
        provider="cohere",
        roles=["coder", "frontend"],
        strengths=["fast"],
        priority=3,
        fallback_priority=4,
        cost="cheap",
        requires_key=True,
        context_window=32000,
    ),
    
    # Lepton (2 models)
    ModelMetadata(
        name="lepton/llama-3.1-405b",
        provider="lepton",
        roles=["planner", "architect", "reviewer"],
        strengths=["reasoning", "long-context"],
        priority=1,
        fallback_priority=2,
        cost="expensive",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="lepton/llama-3.1-8b",
        provider="lepton",
        roles=["coder", "documentation"],
        strengths=["fast", "cheap"],
        priority=3,
        fallback_priority=4,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),
    
    # Additional free models
    ModelMetadata(
        name="perplexity/llama-3.1-sonar-large",
        provider="perplexity",
        roles=["planner", "researcher"],
        strengths=["reasoning"],
        priority=2,
        fallback_priority=3,
        cost="cheap",
        requires_key=True,
        context_window=128000,
    ),
    ModelMetadata(
        name="mistral/open-mixtral-8x22b",
        provider="mistral",
        roles=["planner", "architect", "coder"],
        strengths=["reasoning", "code"],
        priority=1,
        fallback_priority=2,
        cost="expensive",
        requires_key=True,
        context_window=64000,
    ),
]


# Legacy string-based list for backward compatibility
APPROVED_MODELS = [m.name for m in MODEL_REGISTRY]


def get_models_by_role(role: ModelRole) -> List[ModelMetadata]:
    """Get models filtered by role, sorted by priority."""
    filtered = [m for m in MODEL_REGISTRY if role.value in m.roles]
    return sorted(filtered, key=lambda x: x.priority)


def get_models_by_provider(provider: str) -> List[ModelMetadata]:
    """Get models filtered by provider."""
    return [m for m in MODEL_REGISTRY if m.provider == provider]


def get_free_models() -> List[ModelMetadata]:
    """Get all free models."""
    return [m for m in MODEL_REGISTRY if m.cost == "free"]


def get_model_by_name(name: str) -> Optional[ModelMetadata]:
    """Get model by full name."""
    for m in MODEL_REGISTRY:
        if m.name == name:
            return m
    return None


# Task-to-Model Assignment with 20+ Categories
TASK_CATEGORIES = {
    "code_generation": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallback": ["openrouter/deepseek/deepseek-v4-flash:free", "together/qwen-2.5-coder-32b-instruct"],
        "description": "Writing new code, functions, classes"
    },
    "deep_reasoning": {
        "primary": "openrouter/deepseek/deepseek-v4-flash:free",
        "fallback": ["openrouter/google/gemma-4-31b-it:free", "groq/llama-3.3-70b-versatile"],
        "description": "Complex reasoning, planning, analysis"
    },
    "bug_detection": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallback": ["huggingface/WizardCoder-33B", "groq/qwen/qwen3-32b"],
        "description": "Finding and diagnosing bugs"
    },
    "code_review": {
        "primary": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "description": "Reviewing code quality and patterns"
    },
    "test_writing": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallback": ["together/qwen-2.5-coder-32b-instruct", "huggingface/CodeLlama-70B-Instruct"],
        "description": "Generating unit tests, integration tests"
    },
    "refactoring": {
        "primary": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/google/gemma-4-31b-it:free"],
        "description": "Code restructuring, simplification"
    },
    "fast_response": {
        "primary": "groq/llama-3.1-8b-instant",
        "fallback": ["openrouter/meta-llama/llama-3.2-3b-instruct:free", "cloudflare/@cf/mistral/mistral-7b-instruct-v0.2"],
        "description": "Quick answers, simple tasks"
    },
    "long_context": {
        "primary": "openrouter/deepseek/deepseek-v4-flash:free",
        "fallback": ["openrouter/qwen/qwen3-coder:free", "groq/llama-3.3-70b-versatile"],
        "description": "1M+ context tasks, large codebase"
    },
    "api_development": {
        "primary": "together/qwen-2.5-72b-instruct",
        "fallback": ["openrouter/qwen/qwen3-next-80b-a3b-instruct:free", "groq/qwen/qwen3-32b"],
        "description": "REST, GraphQL, backend APIs"
    },
    "frontend_ui": {
        "primary": "openrouter/google/gemma-4-31b-it:free",
        "fallback": ["openrouter/meta-llama/llama-3.3-70b-instruct:free", "gemini/gemini-3.5-flash"],
        "description": "React, Vue, HTML/CSS interfaces"
    },
    "database_sql": {
        "primary": "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        "fallback": ["cohere/command-r-plus", "openrouter/deepseek/deepseek-v4-flash:free"],
        "description": "SQL queries, database design"
    },
    "devops_deployment": {
        "primary": "openrouter/google/gemma-4-31b-it:free",
        "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/meta-llama/llama-3.3-70b-instruct:free"],
        "description": "Docker, Kubernetes, CI/CD"
    },
    "security_audit": {
        "primary": "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        "fallback": ["cohere/command-r-plus", "openrouter/deepseek/deepseek-v4-flash:free"],
        "description": "Security vulnerability scanning"
    },
    "documentation": {
        "primary": "openrouter/meta-llama/llama-3.2-3b-instruct:free",
        "fallback": ["gemini/gemini-2.5-flash", "groq/llama-3.1-8b-instant"],
        "description": "README, docs, comments generation"
    },
    "data_analysis": {
        "primary": "together/qwen-2.5-72b-instruct",
        "fallback": ["huggingface/Qwen2.5-Coder-32B-Instruct", "openrouter/google/gemma-4-31b-it:free"],
        "description": "Pandas, data processing, analytics"
    },
    "ml_ai_tasks": {
        "primary": "huggingface/DeepSeek-Coder-V2",
        "fallback": ["together/deepseek-coder-v2-instruct", "openrouter/deepseek/deepseek-v4-flash:free"],
        "description": "ML models, AI pipelines, training"
    },
    "mobile_development": {
        "primary": "openrouter/google/gemma-4-31b-it:free",
        "fallback": ["openrouter/deepseek/deepseek-v4-flash:free", "gemini/gemini-3.5-flash"],
        "description": "iOS, Android, React Native"
    },
    "performance_optimization": {
        "primary": "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
        "fallback": ["openrouter/qwen/qwen3-coder:free", "huggingface/WizardCoder-33B"],
        "description": "Profiling, optimization, caching"
    },
    "git_operations": {
        "primary": "groq/llama-3.1-8b-instant",
        "fallback": ["openrouter/meta-llama/llama-3.2-3b-instruct:free", "cloudflare/@cf/mistral/mistral-7b-instruct-v0.2"],
        "description": "Git commands, branching, PRs"
    },
    "debugging": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallback": ["huggingface/WizardCoder-33B", "groq/qwen/qwen3-32b"],
        "description": "Stack traces, error fixing"
    },
    "architecture_design": {
        "primary": "openrouter/deepseek/deepseek-v4-flash:free",
        "fallback": ["openrouter/meta-llama/llama-3.3-70b-instruct:free", "together/llama-3.3-70b-instruct"],
        "description": "System design, patterns, microservices"
    },
    "testing_qa": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallback": ["together/qwen-2.5-coder-32b-instruct", "huggingface/CodeLlama-70B-Instruct"],
        "description": "Test execution, QA automation"
    },
    "office_document_generation": {
        "primary": "openrouter/minimax/minimax-m2.5:free",
        "fallback": ["openrouter/meta-llama/llama-3.2-3b-instruct:free", "gemini/gemini-2.5-flash"],
        "description": "Word docs, Excel, PowerPoint, financial templates"
    },
}

# Model roles/configurations (legacy, kept for compatibility)
MODEL_ROLES = {
    "executor": {
        "primary": "openrouter/deepseek/deepseek-v4-flash:free",
        "fallback": ["openrouter/qwen/qwen3-coder:free", "groq/llama-3.3-70b-versatile"],
        "temperature": 0.1,
        "max_tokens": 8192,
    },
    "planner": {
        "primary": "openrouter/deepseek/deepseek-v4-flash:free",
        "fallback": ["openrouter/google/gemma-4-31b-it:free", "gemini/gemini-3.5-flash"],
        "temperature": 0.2,
        "max_tokens": 8192,
    },
    "debugger": {
        "primary": "openrouter/qwen/qwen3-coder:free",
        "fallback": ["huggingface/WizardCoder-33B", "groq/qwen/qwen3-32b"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
    "reviewer": {
        "primary": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
        "fallback": ["groq/llama-3.3-70b-versatile", "openrouter/deepseek/deepseek-v4-flash:free"],
        "temperature": 0.1,
        "max_tokens": 4096,
    },
}