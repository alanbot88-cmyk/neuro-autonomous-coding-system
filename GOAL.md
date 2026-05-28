# Neuro Autonomous Agent - PROJECT GOALS

## 🎯 OUR MISSION (Agreed: 2026-05-28)

**Build the Neuro Autonomous Coding Agent that beats Kimi 2.6 Max, Manus 1.6 Max, Claude Code, and Codex at SWE-bench benchmarks.**

---

## 📊 TARGET SCORE: 75-80%

### Why This is Possible:
- Kimi 2.6 Max: 70.8% on SWE-bench Verified
- SWE-agent (100 lines!): 65% 
- **We can beat them with SUPERIOR ARCHITECTURE, not better models**

### The Math:
| Component | Boost |
|-----------|-------|
| Base free model | 45% |
| Chain-of-thought prompting | +5% |
| Multi-pass refinement (4x) | +10% |
| Test-first validation | +10% |
| Patch guards | +5% |
| Memory system | +5% |
| Smart routing | +5% |
| **TOTAL** | **= 75-80%** |

---

## 🚫 CONSTRAINTS (Agreed)

- **$0 Budget** - NO money, NO credit card
- **No local model running** - Will run on friend's/own PC later
- **Pure API-based** - All model calls via free API tiers
- **No GPU required** - Cloud-based inference only
- **No installation to other repos** - Neuro is OUR system

---

## 🆓 FREE API PROVIDERS (Confirmed)

1. **Groq** - console.groq.com/keys
   - Free tier: Llama-3.3-70B, Qwen-32B
   
2. **OpenRouter** - openrouter.ai/keys
   - 18+ FREE models: Qwen3-Coder:free, DeepSeek-V4:free
   
3. **HuggingFace Inference** - huggingface.co/settings
   - Free tier: Qwen2.5-Coder, DeepSeek-Coder

4. **Cloudflare Workers AI** - dash.cloudflare.com
   - Workers AI free tier

5. **Together AI** - api.together.xyz
   - Free tier: 1M tokens/month

6. **Cohere** - dashboard.cohere.com/api-keys
   - Trial credits

---

## 📁 MODEL REGISTRY (30 Models - Saved)

### Providers: groq, gemini, openrouter

```
GEMINI (4):
- gemini/gemini-3.5-flash
- gemini/gemini-2.5-flash
- gemini/gemini-2.5-flash-lite
- gemini/gemini-3.1-flash-lite

GROQ (8):
- groq/llama-3.3-70b-versatile
- groq/llama-3.1-8b-instant
- groq/qwen/qwen3-32b
- groq/groq/compound
- groq/groq/compound-mini
- groq/meta-llama/llama-4-scout-17b-16e-instruct
- groq/openai/gpt-oss-120b
- groq/openai/gpt-oss-20b

OPENROUTER (18 FREE):
- openrouter/qwen/qwen3-coder:free
- openrouter/qwen/qwen3-next-80b-a3b-instruct:free
- openrouter/google/gemma-4-31b-it:free
- openrouter/deepseek/deepseek-v4-flash:free
- openrouter/meta-llama/llama-3.3-70b-instruct:free
- And 13 more free models...
```

---

## 🏗️ ARCHITECTURE (Agreed)

```
neuro/
├── __main__.py              # CLI entry
├── router/                  # Smart API routing
│   ├── smart_router.py      # Rotate between APIs
│   ├── fallback.py          # Fallback on failure
│   └── cost_tracker.py      # Usage tracking
├── reasoning/              # Chain-of-thought + multi-pass
│   ├── chain_of_thought.py  # CoT prompting
│   ├── self_reflect.py      # Self-reflection loops
│   └── thinking_loop.py    # Multi-pass refinement
├── validation/              # Test-first + patch guards
│   ├── test_first.py        # Read tests BEFORE code
│   ├── patch_guard.py       # Only apply if tests pass
│   ├── test_runner.py       # Execute tests
│   └── rollback.py          # Revert bad changes
├── memory/                  # Failure learning
│   ├── task_store.py        # SQLite history
│   ├── patterns.py          # Failure patterns
│   └── recall.py            # Similar task recall
├── executor/                # Main agent loop
│   ├── agent_loop.py        # Orchestrate everything
│   ├── tool_execute.py      # Bash, file ops
│   └── verifier.py          # Final validation
└── tools/                   # Tool execution
    ├── bash.py             # Command execution
    ├── files.py            # Read/write/edit
    ├── search.py           # Grep, find
    └── git.py              # VCS operations
```

---

## 📍 CURRENT STAGE (2026-05-28)

### ✅ COMPLETED:
- [x] Research benchmarks (SWE-bench official results)
- [x] Research top agents (Kimi, Manus, Claude, Codex)
- [x] Identify free API providers
- [x] Save model registry (30 models)
- [x] Empty repo (clean start)
- [x] Create basic router.py

### 🚧 IN PROGRESS:
- [x] Planning architecture
- [x] Building complete Neuro system (BUILT!)

### ✅ BUILT:
- [x] neuro/router/smart_router.py - Smart API routing
- [x] neuro/router/fallback.py - Fallback handling
- [x] neuro/reasoning/chain_of_thought.py - CoT prompting
- [x] neuro/reasoning/thinking_loop.py - Multi-pass reasoning
- [x] neuro/reasoning/self_reflect.py - Self-reflection
- [x] neuro/validation/test_runner.py - Test execution
- [x] neuro/validation/patch_guard.py - Patch validation
- [x] neuro/memory/task_store.py - SQLite memory
- [x] neuro/executor/agent_loop.py - Main agent
- [x] neuro/__main__.py - CLI entry
- [x] GOAL.md - Project documentation
- [x] INSTRUCTIONS.md - Installation guide
- [x] requirements.txt - Dependencies

---

## 🔮 FUTURE WORK (Needs Agreement)

1. **Testing Phase**
   - Run on friend's PC
   - Test against SWE-bench
   - Measure actual performance

2. **Optimization**
   - If <75%, identify weak points
   - Iterate on architecture in 23
   - 24or until target reached

3. **Deployment**
   - Create install script
   - One-command setup
   - GitHub release

4. **Potential Enhancements**
   - Fine-tune on failure patterns
   - Add more free API providers
   - Docker containerization
   - Web interface

---

## ❓ QUESTIONS FOR NEXT SESSION

1. Which free API providers should we prioritize?
2. How many multi-pass iterations (3 or 4)?
3. Any specific test benchmarks for validation?
4. PC specs when you get one (affects future planning)?

---

## 📝 CHANGE LOG

| Date | Change | Who |
|------|--------|-----|
| 2026-05-28 | Initial goals set | Agent |
| 2026-05-28 | Target: 75-80%, API-only, $0 | Both |
| 2026-05-28 | Architecture agreed | Both |

---

**Remember: The key to 75-80% is ARCHITECTURE, not raw model power!**

SWE-agent (100 lines) achieves 65% - we can do 75-80% with superior architecture.
