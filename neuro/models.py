# Neuro Model Registry - 50+ Models (Free Tier)
# Task-to-Model Assignment with 20+ Categories
# Last saved: 2026-05-29

APPROVED_PROVIDERS = frozenset({
    'gemini', 'groq', 'openrouter', 'together', 'huggingface', 
    'cloudflare', 'cohere', 'lepton', 'mistral', 'perplexity'
})

# All 50+ approved models
APPROVED_MODELS = [
    # Gemini (5 models)
    "gemini/gemini-3.5-flash",
    "gemini/gemini-2.5-flash",
    "gemini/gemini-2.5-flash-lite",
    "gemini/gemini-3.1-flash-lite",
    "gemini/gemini-2.0-flash-exp",
    
    # Groq (6 models)
    "groq/llama-3.3-70b-versatile",
    "groq/llama-3.1-8b-instant",
    "groq/qwen/qwen3-32b",
    "groq/llama-4-scout-17b-16e-instruct",
    "groq/llama-3.2-90b-vision-instruct",
    "groq/mixtral-8x7b-32768",
    
    # OpenRouter FREE (18 models)
    "openrouter/deepseek/deepseek-v4-flash:free",
    "openrouter/qwen/qwen3-coder:free",
    "openrouter/qwen/qwen3-next-80b-a3b-instruct:free",
    "openrouter/google/gemma-4-31b-it:free",
    "openrouter/google/gemma-4-26b-a4b-it:free",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free",
    "openrouter/meta-llama/llama-3.2-3b-instruct:free",
    "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/openai/gpt-oss-120b:free",
    "openrouter/openai/gpt-oss-20b:free",
    "openrouter/liquid/lfm-2.5-1.2b-thinking:free",
    "openrouter/poolside/laguna-m.1:free",
    "openrouter/baidu/cobuddy:free",
    "openrouter/z-ai/glm-4.5-air:free",
    "openrouter/inflection/inflection-3-pi:free",
    "openrouter/mistralai/mistral-nemo:free",
    "openrouter/anthropic/claude-3-haiku:free",
    "openrouter/microsoft phi-4:free",
    
    # OpenRouter FREE - Additional (2 models)
    "openrouter/minimax/minimax-m2.5:free",
    
    # Together AI (5 models)
    "together/llama-3.3-70b-instruct",
    "together/qwen-2.5-72b-instruct",
    "together/qwen-2.5-coder-32b-instruct",
    "together/mixtral-8x7b-instruct",
    "together/deepseek-coder-v2-instruct",
    
    # HuggingFace (5 models)
    "huggingface/Qwen2.5-Coder-32B-Instruct",
    "huggingface/DeepSeek-Coder-V2",
    "huggingface/CodeLlama-70B-Instruct",
    "huggingface/Starcoder2-15B",
    "huggingface/WizardCoder-33B",
    
    # Cloudflare (3 models)
    "cloudflare/@cf/meta/llama-3.1-70b-instruct",
    "cloudflare/@cf/mistral/mistral-7b-instruct-v0.2",
    "cloudflare/@cf/deepseek-ai/deepseek-coder-6.7b",
    
    # Cohere (3 models)
    "cohere/command-r-plus",
    "cohere/command-r",
    "cohere/command",
    
    # Lepton (2 models)
    "lepton/llama-3.1-405b",
    "lepton/llama-3.1-8b",
    
    # Additional free models (5+)
    "perplexity/llama-3.1-sonar-large",
    "mistral/open-mixtral-8x22b",
]

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