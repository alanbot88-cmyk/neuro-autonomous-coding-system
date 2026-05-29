# Neuro Autonomous Agent - INSTALLATION & USAGE GUIDE 🔒 LOCKED

## Quick Setup

```bash
# 1. Clone the repo
git clone https://github.com/alanbot88-cmyk/neuro-autonomous-coding-system.git
cd neuro-autonomous-coding-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API Keys (NO credit card required!)
# Get your keys from the respective platforms

# Gemini (Google AI Studio) - FREE tier with generous limits
export GEMINI_API_KEY="your-gemini-api-key"

# Groq - FREE tier (30 req/min)
export GROQ_API_KEY="your-groq-api-key"

# OpenRouter - FREE credits available
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Optional: Together AI ($5 free credits)
export TOGETHER_API_KEY="your-together-api-key"

# Optional: Cohere (Trial credits)
export COHERE_API_KEY="your-cohere-api-key"

# Optional: HuggingFace
export HF_TOKEN="your-hf-token"

# Optional: Cloudflare Workers AI
export CLOUDFLARE_API_TOKEN="your-cf-token"

# 4. Run Neuro
PYTHONPATH=. python -m neuro --goal "Fix the bug in main.py"

# Or use CLI
python -m neuro "Add user authentication"
```

---

## 📋 PREREQUISITES

### Required:
- Python 3.10+
- pip
- Git
- API keys (all FREE, no credit card)

### NOT Required:
- GPU/Local models (all via API)
- Credit card
- Money

---

## 🔑 API KEY SETUP (Step by Step)

### Step 1: Get Gemini API Key (⭐ RECOMMENDED - Generous Free Tier)

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy key
5. Add to environment:
```bash
export GEMINI_API_KEY="AIza...."
```

**Gemini Free Tier Includes:**
- gemini-3-flash-preview (latest, cutting-edge)
- gemini-3.5-flash (advanced reasoning)
- gemini-2.5-flash (fast, reliable)
- gemini-1.5-pro (2M context!)
- gemini-1.5-flash (cost-efficient)
- gemini-exp-1206 (experimental)

### Step 2: Get Groq API Key (⭐ Fast Inference)

1. Go to: https://console.groq.com/keys
2. Sign up with email (FREE)
3. Click "Create API Key"
4. Copy key
5. Add to environment:
```bash
export GROQ_API_KEY="gsk_xxxxx"
```

**Groq Free Tier Includes:**
- llama-3.3-70b-versatile (fast 70B)
- llama-3.1-8b-instant (ultra-fast)
- qwen3-32b (balanced)
- mixtral-8x7b (fast MoE)

### Step 3: Get OpenRouter API Key

1. Go to: https://openrouter.ai/keys
2. Sign up (FREE)
3. Create key
4. FREE models available:
   - deepseek/deepseek-v4-flash:free ⭐ (Best coder, 1M context!)
   - qwen/qwen3-coder:free ⭐ (480B MoE)
   - meta-llama/llama-3.3-70b-instruct:free
   - google/gemma-4-31b-it:free
   - And 15+ more!

```bash
export OPENROUTER_API_KEY="sk-or-v1-xxxxx"
```

### Step 4: Optional - Together AI

1. Go to: https://api.together.xyz/
2. Sign up for free tier ($5 credits)
3. Get API key

```bash
export TOGETHER_API_KEY="xxxxx"
```

### Step 5: Optional - Cohere

1. Go to: https://dashboard.cohere.com/api-keys
2. Create trial key
3. Get API key

```bash
export COHERE_API_KEY="xxxxx"
```

### Save Keys Permanently:

```bash
# Add to ~/.bashrc or ~/.zshrc
cat >> ~/.bashrc << 'EOF'
export GEMINI_API_KEY="your-gemini-key"
export GROQ_API_KEY="your-groq-key"
export OPENROUTER_API_KEY="your-openrouter-key"
export TOGETHER_API_KEY="your-together-key"
export COHERE_API_KEY="your-cohere-key"
export HF_TOKEN="your-hf-token"
export CLOUDFLARE_API_TOKEN="your-cf-token"
EOF

source ~/.bashrc
```

---

## 🚀 USAGE

### Basic CLI:

```bash
# Simple task
PYTHONPATH=. python -m neuro --goal "Add print statement to hello.py"

# With specific model
PYTHONPATH=. python -m neuro --goal "Fix authentication bug" --model groq/llama-3.3-70b

# Ask for confirmation before changes
PYTHONPATH=. python -m neuro --goal "Refactor main.py" --confirm

# JSON output for automation
PYTHONPATH=. python -m neuro --goal "Fix bug" --json-output result.json
```

### Programming API:

```python
from neuro import NeuroAgent

agent = NeuroAgent(
    goal="Fix the login bug",
    working_dir="/path/to/project",
    max_steps=50
)

result = agent.run()
print(f"Success: {result.success}")
print(f"Files changed: {result.files_changed}")
```

---

## 🎯 TARGET SCORE: 75-80%

### How We Achieve It:

```
1. Chain-of-Thought: Forces step-by-step reasoning
2. Multi-Pass: 4 iterations to converge on solution  
3. Test-First: Read tests before writing code
4. Patch Guards: Only apply if tests pass
5. Memory: Learn from past failures
6. Smart Routing: Best model for each task
```

### Benchmarking:

```bash
# Run on SWE-bench
PYTHONPATH=. python -m neuro.benchmark --suite swe-bench-verified

# Run specific tests
PYTHONPATH=. python -m neuro.test --tests tests/python/

# Measure performance
PYTHONPATH=. python -m neuro.evaluate --goal "Fix Django bug"
```

---

## 🔧 ARCHITECTURE

```
neuro/
├── router/          # API routing
├── reasoning/       # CoT + multi-pass
├── validation/      # Tests + patches
├── memory/         # Learning
├── executor/       # Main loop
└── tools/          # Bash, files, git
```

---

## 📦 PROJECT STRUCTURE

```bash
neuro/
├── __init__.py          # Package init
├── __main__.py          # CLI entry
├── py.typed             # Type hints marker
│
├── router/              # Model routing
│   ├── __init__.py
│   ├── smart_router.py  # Main router
│   ├── fallback.py      # Fallback handling
│   └── cost_tracker.py  # Usage tracking
│
├── reasoning/           # Reasoning loops
│   ├── __init__.py
│   ├── chain_of_thought.py
│   ├── self_reflect.py
│   └── thinking_loop.py
│
├── validation/          # Tests + patches
│   ├── __init__.py
│   ├── test_first.py
│   ├── patch_guard.py
│   ├── test_runner.py
│   └── rollback.py
│
├── memory/              # Persistence
│   ├── __init__.py
│   ├── task_store.py
│   ├── patterns.py
│   └── recall.py
│
├── executor/            # Core agent
│   ├── __init__.py
│   ├── agent_loop.py
│   ├── tool_execute.py
│   └── verifier.py
│
└── tools/               # Tool execution
    ├── __init__.py
    ├── bash.py
    ├── files.py
    ├── search.py
    └── git.py
```

---

## 🐛 TROUBLESHOOTING

### "No API key found" Error

```bash
# Check keys are set
env | grep -E "GEMINI|GROQ|OPENROUTER"

# Set keys
export GEMINI_API_KEY="your-key"
export GROQ_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
```

### "Rate limit exceeded"

```bash
# Wait and retry, or add more API providers
# The router will automatically switch to backup providers
```

### "Module not found"

```bash
# Run with PYTHONPATH
PYTHONPATH=. python -m neuro

# Or install in dev mode
pip install -e .
```

### "Permission denied"

```bash
# Check file permissions
chmod +x neuro/__main__.py
```

---

## 📊 MONITORING

### Check API usage:

```bash
# View cost tracking
PYTHONPATH=. python -m neuro.router.stats

# Check which APIs are working
PYTHONPATH=. python -m neuro.router.health
```

### View task history:

```bash
# SQLite database created in ~/.neuro/
ls ~/.neuro/
# task_history.db

# Query it
sqlite3 ~/.neuro/task_history.db "SELECT * FROM tasks LIMIT 10;"
```

---

## 🔄 UPDATE GUIDE

### Update Neuro:

```bash
cd neuro-autonomous-coding-system
git pull origin main
pip install -r requirements.txt --upgrade
```

### Update API keys:

```bash
# Edit ~/.bashrc with new keys
nano ~/.bashrc
source ~/.bashrc
```

---

## 🌐 ADD NEW API PROVIDERS

Edit `neuro/router/smart_router.py`:

```python
class SmartRouter:
    PROVIDERS = [
        # Add new provider here
        ("provider_name", "https://api.provider.com", "api_key_env_var"),
        # Format: (name, base_url, env_var_name)
    ]
```

---

## 📖 MORE DOCUMENTATION

- [GOAL.md](./GOAL.md) - Project goals and progress
- [README.md](./README.md) - Main readme
- [docs/](docs/) - Detailed docs

---

## 💡 TIPS

1. **Start with Groq** - Fastest, most reliable free tier
2. **Add OpenRouter** - Best free models (Qwen3-Coder:free)
3. **Use memory** - System learns over time
4. **Be specific in goals** - "Fix SQL injection in login.py" > "fix bug"
5. **Multiple small tasks** - Better than one big task

### Example Goals:

✅ Good:
- "Add input validation to user registration form"
- "Fix memory leak in image loader"
- "Optimize database query in search function"

❌ Bad:
- "fix the thing"
- "make it work"
- "improve code"

---

## 🆘 HELP

### Run diagnostics:

```bash
PYTHONPATH=. python -m neuro.diag
```

### View logs:

```bash
cat ~/.neuro/logs/neuro.log
```

### Check version:

```bash
python -m neuro --version
```

---

## �️ PERFORMANCE TIPS

1. **Use --no-apply** to preview without changes
2. **Use --max-steps 10** for quick tasks
3. **Use --dry-run** for testing
4. **Use --profile** to measure time

---

## 📝 COMMON COMMANDS

```bash
# Install
make install

# Run
make run GOAL="Fix bug"

# Test
make test

# Benchmark
make benchmark

# Clean
make clean
```

---

**Last Updated: 2026-05-29**
**Version: 0.2.0**

**Features: 50+ FREE API Models, Gemini 3.5 Flash, DeepSeek V4 Flash, Qwen3 Coder, 100+ Auto-trigger Skills**
