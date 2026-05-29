"""
🧠 NEURO MAIN BRAIN - PERMANENT MODEL ASSIGNMENTS (LOCKED 🔒)
==============================================================
This file defines the MAIN BRAIN configuration for Neuro.

⚠️  🔒 LOCKED - ALL ASSIGNMENTS ARE PERMANENT!
⚠️  DO NOT CHANGE THESE ASSIGNMENTS WITHOUT USER REQUEST!
⚠️  These models are the permanent brain of the system.

Last Updated: 2026-05-29
Status: 🔒 LOCKED - DO NOT MODIFY UNLESS USER REQUESTS

API KEYS REQUIRED:
- GEMINI_API_KEY (Google AI Studio) - Primary brain key
- GROQ_API_KEY (Groq) - Fast inference
- OPENROUTER_API_KEY (OpenRouter) - Best coding models
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict


# =============================================================================
# 🧠 MAIN BRAIN - PERMANENT MODEL CONFIGURATION
# =============================================================================

class BrainModel(Enum):
    """Main brain models - DO NOT CHANGE!"""
    # Primary Brain Models (Gemini)
    GEMINI_3_FLASH_PREVIEW = "gemini-3-flash-preview"
    GEMINI_3_5_FLASH = "gemini-3.5-flash"
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_FLASH_8B = "gemini-1.5-flash-8b"
    GEMINI_EXP_1206 = "gemini-exp-1206"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    
    # Groq Models (Fast Inference)
    GROQ_LLAMA_3_3_70B = "groq-llama-3.3-70b-versatile"
    GROQ_LLAMA_3_1_8B = "groq-llama-3.1-8b-instant"
    GROQ_QWEN3_32B = "groq-qwen3-32b"
    GROQ_MIXTRAL_8X7B = "groq-mixtral-8x7b-32768"
    
    # OpenRouter Models (Best for Coding)
    OR_DEEPSEEK_V4_FLASH = "openrouter-deepseek-v4-flash"
    OR_QWEN3_CODER = "openrouter-qwen3-coder"
    OR_LLAMA_3_3_70B = "openrouter-llama-3.3-70b"
    
    # Together AI (Specialized Coders)
    TOGETHER_QWEN_CODER = "together-qwen-2.5-coder-32b"


@dataclass
class TaskBrainConfig:
    """Permanent task-to-model assignment for main brain."""
    task_name: str
    primary_model: str
    fallback_1: str
    fallback_2: str
    primary_reason: str
    is_gemini_primary: bool = False


# =============================================================================
# 🎯 PERMANENT TASK ASSIGNMENTS - MAIN BRAIN
# =============================================================================

MAIN_BRAIN_TASKS: List[TaskBrainConfig] = [
    
    # =========================================================================
    # 🧠 DEEP REASONING - GEMINI 3.5 FLASH AS PRIMARY
    # =========================================================================
    TaskBrainConfig(
        task_name="Deep Reasoning",
        primary_model="gemini-3.5-flash",
        fallback_1="gemini-3-flash-preview",
        fallback_2="gemini-2.5-flash",
        primary_reason="Advanced reasoning, 1M context, cutting-edge features, latest Gemini",
        is_gemini_primary=True
    ),
    
    # =========================================================================
    # 💻 CODE GENERATION - DEEPSEEK V4 FLASH (BEST CODER)
    # =========================================================================
    TaskBrainConfig(
        task_name="Code Generation",
        primary_model="openrouter-deepseek-v4-flash",
        fallback_1="gemini-3.5-flash",
        fallback_2="together-qwen-2.5-coder-32b",
        primary_reason="Best coding model (39.8% on SWE-bench), 1M context, agentic",
        is_gemini_primary=False
    ),
    
    # =========================================================================
    # 🐛 BUG DETECTION - QWEN3 CODER (MoE - 480B PARAMS)
    # =========================================================================
    TaskBrainConfig(
        task_name="Bug Detection",
        primary_model="openrouter-qwen3-coder",
        fallback_1="gemini-3.5-flash",
        fallback_2="openrouter-deepseek-v4-flash",
        primary_reason="MoE model (480B params), excellent at code analysis and pattern recognition",
        is_gemini_primary=False
    ),
    
    # =========================================================================
    # 👀 CODE REVIEW - LLAMA 3.3 70B
    # =========================================================================
    TaskBrainConfig(
        task_name="Code Review",
        primary_model="openrouter-llama-3.3-70b",
        fallback_1="groq-llama-3.3-70b-versatile",
        fallback_2="gemini-3.5-flash",
        primary_reason="70B model with excellent review capability and context understanding",
        is_gemini_primary=False
    ),
    
    # =========================================================================
    # 🧪 TEST WRITING - QWEN 2.5 CODER 32B
    # =========================================================================
    TaskBrainConfig(
        task_name="Test Writing",
        primary_model="together-qwen-2.5-coder-32b",
        fallback_1="openrouter-qwen3-coder",
        fallback_2="gemini-3.5-flash",
        primary_reason="Specialized coder model optimized for understanding code structure and patterns",
        is_gemini_primary=False
    ),
    
    # =========================================================================
    # 📜 LONG CONTEXT - DEEPSEEK V4 FLASH (1M TOKENS!)
    # =========================================================================
    TaskBrainConfig(
        task_name="Long Context",
        primary_model="openrouter-deepseek-v4-flash",
        fallback_1="gemini-1.5-pro",
        fallback_2="gemini-3.5-flash",
        primary_reason="1M token context window, excellent at long documents and repositories",
        is_gemini_primary=False
    ),
    
    # =========================================================================
    # 🖼️ MULTIMODAL - GEMINI 2.5 FLASH
    # =========================================================================
    TaskBrainConfig(
        task_name="Multimodal",
        primary_model="gemini-2.5-flash",
        fallback_1="gemini-1.5-pro",
        fallback_2="gemini-3.5-flash",
        primary_reason="Native multimodal support, fast, reliable, 1M context for images/docs",
        is_gemini_primary=True
    ),
    
    # =========================================================================
    # ⚡ FAST RESPONSE - GROQ LLAMA 3.1 8B
    # =========================================================================
    TaskBrainConfig(
        task_name="Fast Response",
        primary_model="groq-llama-3.1-8b-instant",
        fallback_1="gemini-1.5-flash-8b",
        fallback_2="openrouter-llama-3.2-3b",
        primary_reason="Ultra-fast inference, optimized for speed (Groq infrastructure)",
        is_gemini_primary=False
    ),
    
    # =========================================================================
    # 🔀 AGENT SWARM - GEMINI 3.5 FLASH
    # =========================================================================
    TaskBrainConfig(
        task_name="Agent Swarm",
        primary_model="gemini-3.5-flash",
        fallback_1="groq-llama-3.3-70b-versatile",
        fallback_2="openrouter-deepseek-v4-flash",
        primary_reason="Fast, cheap, supports parallel execution, excellent reasoning for multi-agent",
        is_gemini_primary=True
    ),
    
    # =========================================================================
    # ✅ SIMPLE TASK - GEMINI 1.5 FLASH
    # =========================================================================
    TaskBrainConfig(
        task_name="Simple Task",
        primary_model="gemini-1.5-flash",
        fallback_1="groq-llama-3.1-8b-instant",
        fallback_2="gemini-2.5-flash",
        primary_reason="Cost-effective, fast, reliable for simple straightforward tasks",
        is_gemini_primary=True
    ),
]


# =============================================================================
# 🔄 FALLBACK CHAINS - PERMANENT
# =============================================================================

PERMANENT_FALLBACK_CHAINS: Dict[str, List[str]] = {
    "coding": [
        "openrouter-deepseek-v4-flash",  # Best coder
        "together-qwen-2.5-coder-32b",  # Specialized coder
        "openrouter-qwen3-coder",        # MoE coder
        "gemini-3.5-flash",              # Gemini for reasoning
        "openrouter-llama-3.3-70b",      # 70B model
    ],
    
    "reasoning": [
        "gemini-3.5-flash",              # PRIMARY - Advanced reasoning
        "gemini-3-flash-preview",        # Latest features
        "openrouter-deepseek-v4-flash",  # Agentic
        "cohere-command-r-plus",         # Tool use
        "openrouter-llama-3.3-70b",      # 70B
    ],
    
    "fast": [
        "groq-llama-3.1-8b-instant",     # Fastest (Groq)
        "gemini-1.5-flash-8b",           # Efficient
        "openrouter-llama-3.2-3b",       # Small fast
        "gemini-2.5-flash",              # Reliable
    ],
    
    "long_context": [
        "openrouter-deepseek-v4-flash",  # 1M tokens
        "gemini-1.5-pro",                # 2M tokens
        "gemini-3.5-flash",              # 1M tokens
        "cohere-command-r-plus",         # 128K context
    ],
    
    "multimodal": [
        "gemini-2.5-flash",              # PRIMARY - Native multimodal
        "gemini-1.5-pro",                # Larger context
        "gemini-3.5-flash",              # Reasoning
        "openrouter-deepseek-v4-flash",  # General
    ],
    
    "default": [
        "gemini-3.5-flash",              # PRIMARY - Best all-rounder
        "gemini-2.5-flash",              # Reliable
        "openrouter-deepseek-v4-flash",  # Best coding
        "openrouter-llama-3.3-70b",     # 70B
        "groq-llama-3.3-70b-versatile",  # Fast 70B
    ],
}


# =============================================================================
# 🎯 MODEL CAPABILITIES MATRIX
# =============================================================================

MODEL_CAPABILITIES: Dict[str, Dict] = {
    # GEMINI MODELS (Primary Brain)
    "gemini-3.5-flash": {
        "primary_tasks": ["Deep Reasoning", "Agent Swarm"],
        "strengths": ["advanced_reasoning", "coding", "analysis", "multimodal", "fast"],
        "context_window": "1M tokens",
        "is_primary_brain": True,
        "provider": "gemini"
    },
    
    "gemini-2.5-flash": {
        "primary_tasks": ["Multimodal", "General"],
        "strengths": ["fast", "coding", "reasoning", "multimodal", "long_context", "reliable"],
        "context_window": "1M tokens",
        "is_primary_brain": True,
        "provider": "gemini"
    },
    
    "gemini-1.5-flash": {
        "primary_tasks": ["Simple Task"],
        "strengths": ["fast", "coding", "reasoning", "cost_effective"],
        "context_window": "1M tokens",
        "is_primary_brain": True,
        "provider": "gemini"
    },
    
    "gemini-1.5-pro": {
        "primary_tasks": ["Long Context"],
        "strengths": ["complex_reasoning", "long_context", "coding", "2M_tokens"],
        "context_window": "2M tokens",
        "is_primary_brain": True,
        "provider": "gemini"
    },
    
    # OPENROUTER MODELS (Best for Coding)
    "openrouter-deepseek-v4-flash": {
        "primary_tasks": ["Code Generation", "Long Context"],
        "strengths": ["coding", "reasoning", "long_context", "agentic", "best_coder"],
        "context_window": "1M tokens",
        "is_primary_brain": True,
        "provider": "openrouter"
    },
    
    "openrouter-qwen3-coder": {
        "primary_tasks": ["Bug Detection"],
        "strengths": ["coding", "MoE", "code_generation", "bug_detection", "480b_moe"],
        "context_window": "128K tokens",
        "is_primary_brain": True,
        "provider": "openrouter"
    },
    
    "openrouter-llama-3.3-70b": {
        "primary_tasks": ["Code Review"],
        "strengths": ["general", "reasoning", "coding", "70b"],
        "context_window": "128K tokens",
        "is_primary_brain": True,
        "provider": "openrouter"
    },
    
    # GROQ MODELS (Fast Inference)
    "groq-llama-3.1-8b-instant": {
        "primary_tasks": ["Fast Response"],
        "strengths": ["ultra_fast", "quick_responses", "efficient", "fastest"],
        "context_window": "128K tokens",
        "is_primary_brain": True,
        "provider": "groq"
    },
    
    "groq-llama-3.3-70b-versatile": {
        "primary_tasks": ["Code Review (fallback)", "Agent Swarm (fallback)"],
        "strengths": ["fast_inference", "coding", "reasoning", "70b"],
        "context_window": "128K tokens",
        "is_primary_brain": True,
        "provider": "groq"
    },
    
    # TOGETHER AI (Specialized Coder)
    "together-qwen-2.5-coder-32b": {
        "primary_tasks": ["Test Writing"],
        "strengths": ["coding", "code_generation", "debugging", "specialized_coder"],
        "context_window": "128K tokens",
        "is_primary_brain": True,
        "provider": "together"
    },
}


# =============================================================================
# 🔧 UTILITY FUNCTIONS - DO NOT CHANGE BEHAVIOR
# =============================================================================

def get_brain_config_for_task(task_name: str) -> TaskBrainConfig:
    """Get permanent brain config for a task."""
    for task in MAIN_BRAIN_TASKS:
        if task.task_name.lower() == task_name.lower():
            return task
    # Default to Deep Reasoning
    return MAIN_BRAIN_TASKS[0]


def get_fallback_chain_for_task(task_name: str) -> List[str]:
    """Get fallback chain for a task."""
    task_lower = task_name.lower()
    
    if "code" in task_lower and ("generat" in task_lower or "writ" in task_lower):
        return PERMANENT_FALLBACK_CHAINS["coding"]
    elif "reason" in task_lower or "think" in task_lower or "analy" in task_lower:
        return PERMANENT_FALLBACK_CHAINS["reasoning"]
    elif "fast" in task_lower or "quick" in task_lower:
        return PERMANENT_FALLBACK_CHAINS["fast"]
    elif "long" in task_lower or "context" in task_lower or "large" in task_lower:
        return PERMANENT_FALLBACK_CHAINS["long_context"]
    elif "multi" in task_lower or "image" in task_lower or "vision" in task_lower:
        return PERMANENT_FALLBACK_CHAINS["multimodal"]
    else:
        return PERMANENT_FALLBACK_CHAINS["default"]


def is_gemini_primary_task(task_name: str) -> bool:
    """Check if task uses Gemini as primary model."""
    config = get_brain_config_for_task(task_name)
    return config.is_gemini_primary


def get_primary_model_for_task(task_name: str) -> str:
    """Get the primary model for a task from main brain."""
    config = get_brain_config_for_task(task_name)
    return config.primary_model


def get_all_primary_brain_models() -> List[str]:
    """Get all primary brain models."""
    return [task.primary_model for task in MAIN_BRAIN_TASKS]


def get_gemini_primary_tasks() -> List[str]:
    """Get tasks where Gemini is the primary model."""
    return [task.task_name for task in MAIN_BRAIN_TASKS if task.is_gemini_primary]


# =============================================================================
# 📊 SUMMARY
# =============================================================================

def print_brain_summary() -> str:
    """Print main brain configuration summary."""
    summary = """
╔══════════════════════════════════════════════════════════════════════╗
║                    🧠 NEURO MAIN BRAIN CONFIG 🧠                      ║
║                                                                      ║
║  ⚠️  PERMANENT CONFIGURATION - DO NOT CHANGE UNLESS USER REQUESTS    ║
╚══════════════════════════════════════════════════════════════════════╝

GEMINI PRIMARY TASKS (Use Gemini API):
  🧠 Deep Reasoning → gemini-3.5-flash (PRIMARY)
  🖼️ Multimodal → gemini-2.5-flash (PRIMARY)
  🔀 Agent Swarm → gemini-3.5-flash (PRIMARY)
  ✅ Simple Task → gemini-1.5-flash (PRIMARY)
  📜 Long Context → gemini-1.5-pro (fallback) | gemini-3.5-flash

CODING PRIMARY TASKS (Use OpenRouter/Together):
  💻 Code Generation → openrouter-deepseek-v4-flash (BEST CODER)
  🐛 Bug Detection → openrouter-qwen3-coder (MoE - 480B)
  👀 Code Review → openrouter-llama-3.3-70b (70B model)
  🧪 Test Writing → together-qwen-2.5-coder-32b (Specialized)

FAST TASKS (Use Groq):
  ⚡ Fast Response → groq-llama-3.1-8b-instant (FASTEST)

┌─────────────────────────────────────────────────────────────────────┐
│  KEY: Gemini is the MAIN BRAIN for reasoning and multimodal tasks  │
│       OpenRouter/Together are SPECIALISTS for coding tasks          │
│       Groq is for SPEED when you need fast responses                │
└─────────────────────────────────────────────────────────────────────┘
"""
    return summary


# =============================================================================
# VERIFICATION
# =============================================================================

if __name__ == "__main__":
    print(print_brain_summary())
    
    print("\n📋 ALL TASKS AND PRIMARY MODELS:")
    for task in MAIN_BRAIN_TASKS:
        emoji = "🔵" if task.is_gemini_primary else "🟢"
        print(f"  {emoji} {task.task_name}: {task.primary_model}")
    
    print("\n✅ Gemini Primary Tasks:", get_gemini_primary_tasks())
    print("✅ All Primary Models:", get_all_primary_brain_models())