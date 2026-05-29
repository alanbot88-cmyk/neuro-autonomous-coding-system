# Neuro - Autonomous Coding System

An intelligent multi-model routing agent system with automatic skill integration.
Neuro is a brain-inspired autonomous engineering runtime designed to build production-grade apps.

## ⚠️ HONEST STATUS

**Current Status**: Neuro has a working core loop for autonomous coding.

**What's Real**:
- ✅ Multi-provider model routing (Groq, OpenRouter, Gemini, Together, HuggingFace, Cloudflare)
- ✅ 50+ model registry with structured metadata and role-based selection
- ✅ Staged cognitive routing (planner → coder → debugger → validator)
- ✅ Structured edit format for machine-parseable file changes
- ✅ Command execution with validation
- ✅ Error repair loop
- ✅ Local mini eval harness (smoke tests, NOT official benchmarks)
- ✅ Safe file writing with workspace boundary enforcement

**What's NOT Claimed**:
- ❌ Official HumanEval scores (not tested yet)
- ❌ Official SWE-bench scores (not tested yet)
- ❌ "Beats Kimi/Manus/Claude Code" (not proven)
- ❌ 75-85% benchmark performance (target, not achieved)

**Target**: Build toward competitive autonomous coding performance using free/fallback model routing.

## Architecture

### Core Loop
```
Task intake → Repo scan → Planning → File selection → Structured edit generation
    → Safe file writing → Command execution → Test/build validation
    → Error analysis → Repair loop → Final diff summary
```

### Model System
- **50+ models** across 8+ providers
- **Role-based routing**: Planner, Architect, Coder, Debugger, Validator, Reviewer, Frontend, Documentation
- **Fallback chains**: Primary model → same provider next key → different provider → generic fallback
- **Free-first execution**: Prioritizes free models before paid
- **Key rotation**: Supports comma-separated multi-key configuration

### Supported Providers
| Provider | Models | Key Env Vars |
|----------|--------|--------------|
| Groq | 6 | GROQ_API_KEY, GROQ_API_KEYS |
| OpenRouter | 20+ | OPENROUTER_API_KEY, OPENROUTER_API_KEYS |
| Gemini | 5 | GEMINI_API_KEY, GEMINI_API_KEYS, GOOGLE_API_KEY |
| Together | 5 | TOGETHER_API_KEY, TOGETHER_API_KEYS |
| HuggingFace | 5 | HF_TOKEN, HUGGINGFACE_API_KEY |
| Cloudflare | 3 | CLOUDFLARE_AI_API_TOKEN |

Note: Qwen and DeepSeek models are accessed via OpenRouter keys.

## Features

- **Smart Router**: Routes tasks to 50+ AI models based on task type and role
- **Structured Edit Format**: Machine-parseable JSON for file changes
- **Safe File Writer**: Workspace boundary enforcement, backup, dry-run mode
- **Command Runner**: Captures stdout/stderr, timeout, dangerous command blocking
- **Error Repair Loop**: Analyzes failures, generates fixes, re-validates
- **Memory System**: Stores task history, model performance, fallback events
- **Mini Eval Harness**: Local smoke tests for autonomous coding capability

## Usage

### Basic Autonomous Coding
```python
from neuro.tools import AutonomousEditLoop, parse_structured_edit

# Create edit loop
loop = AutonomousEditLoop("/path/to/project", dry_run=False)

# Parse model's structured edit
edit, errors = parse_structured_edit(model_response)

# Apply and validate
result = loop.execute_and_validate(edit)
```

### Router Usage
```python
from neuro.router.smart_router import SmartRouter, Provider

router = SmartRouter()
result = router.complete(
    messages=[{"role": "user", "content": "Fix the bug"}],
    model="openrouter/qwen/qwen3-coder:free"
)
```

### Model Registry
```python
from neuro.models import (
    MODEL_REGISTRY,
    get_models_by_role,
    get_free_models,
    ModelRole,
)

# Get coder models sorted by priority
coders = get_models_by_role(ModelRole.CODER)

# Get all free models
free_models = get_free_models()
```

### Mini Eval Harness
```python
from neuro.validation.mini_eval import run_mini_evals

# Run local smoke tests (NOT official benchmarks)
summary = run_mini_evals()
print(f"Passed: {summary['passed']}/{summary['total']}")
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_neuro_fixes.py -v

# Run mini evals
python -m neuro.validation.mini_eval
```

## Environment Variables

```bash
# Required for providers (at least one needed)
GROQ_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

# Multiple keys (comma-separated)
GROQ_API_KEYS=key1,key2,key3

# Optional providers
TOGETHER_API_KEY=your_key
HF_TOKEN=your_token
CLOUDFLARE_AI_API_TOKEN=your_token
```

## License

MIT
