# Neuro: Flagship AI Capabilities Research

**Goal:** Beat Kimi 2.6 Max, Manus 1.6 Max, Claude Code, GPT-5 on SWE-bench 75-80%
**Constraint:** $0 budget, email-only APIs only
**Updated:** 2026-05-28

---

## 1. COMPETITOR ANALYSIS

### 1.1 Kimi K2.5 (Moonshot AI) - 76.8% SWE-bench

**Architecture:**
- 1 Trillion total parameters (MoE - Mixture of Experts)
- 32 Billion activated parameters
- 384 experts, 8 selected per token
- 256K context length
- Native multimodal (vision + text)
- Vision encoder: MoonViT (400M params)

**Key Capabilities:**

| Capability | Status | Neuro Implementation |
|------------|--------|---------------------|
| Thinking Mode | ✅ | Chain-of-thought + multi-pass |
| Instant Mode | ✅ | Fast response path |
| Agent Swarm | ✅ | Parallel sub-agents |
| Tool Use (search, code, browser) | ✅ | CLI/bash + file ops |
| Multi-modal Input | ✅ | Vision support planned |
| Native Multimodality | ✅ | Future enhancement |
| Code from Vision | ✅ | UI → code (future) |
| Context Management | ✅ | Threshold truncation |

**SWE-bench Score: 76.8%** (5 runs averaged)

**Key Innovations:**
1. Agent Swarm: Main agent decomposes → sub-agents execute → results synthesized
2. Tool-augmented HLE: +20% improvement with tools
3. BrowseComp Agent Swarm: 78.4% (vs 60.6% single agent)
4. Context management: Discard old when threshold exceeded

**Open Source:** https://github.com/MoonshotAI/Kimi-K2.5

---

### 1.2 Manus AI Agent

**Key Features:**
1. **General AI Agent** - Executes tasks, not just Q&A
2. **Multi-model orchestration** - Uses Claude, GPT, etc.
3. **Browser automation** - Can browse and interact with web
4. **File operations** - Read/write/execute files
5. **Workflow automation** - Chains multiple actions
6. **Persistent memory** - Remembers context across sessions
7. **Planning and execution loop** - Decompose → Execute → Verify

**Architecture:**
- Orchestrates multiple models dynamically
- Built-in planning with sub-task decomposition
- Tool use for real-world actions
- Memory-augmented execution

---

### 1.3 Claude Code - ~70% SWE-bench

**Key Features:**
1. **Codebase-aware** - Reads entire codebase
2. **Multi-file editing** - Makes changes across files
3. **Terminal access** - Runs commands, tests
4. **Git operations** - Commit, branch, diff
5. **Search and replace** - Pattern-based edits
6. **Test generation** - Writes and runs tests
7. **Iterative refinement** - Retry on failure

**Architecture:**
- Uses Claude Sonnet/Opus models
- Tool use (bash, editor, search)
- Test-first validation loop
- Observes → Debugs → Fixes loop

---

### 1.4 GPT-5 (OpenAI) - 80.0% SWE-bench

**Key Features:**
1. **Extended thinking** - xhigh reasoning effort
2. **Tool use** - Browsing, code execution
3. **Multimodal** - Vision, audio, text
4. **Long context** - 1M+ token context
5. **Agentic workflows** - Autonomous task completion
6. **Multi-step reasoning** - Plan → Execute → Verify

**SWE-bench Score: 80.0%**

---

### 1.5 Comparison Table

| Feature | Kimi K2.5 | Manus | Claude | GPT-5 | Neuro |
|---------|-----------|-------|--------|-------|-------|
| SWE-bench | 76.8% | ? | ~70% | 80.0% | 70-75% target |
| Thinking Mode | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| Agent Swarm | ✅ | ⚠️ | ❌ | ❌ | ✅ |
| Tool Use | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-model | ⚠️ | ✅ | ❌ | ❌ | ✅ |
| Memory | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ |
| Test-first | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| Context Mgmt | ✅ | ? | ? | ✅ | ✅ |
| Vision | ✅ | ⚠️ | ❌ | ✅ | Future |

---

## 2. FREE API PROVIDERS (Email-Only, No Card)

### 2.1 All Free Providers

| Provider | URL | Free Models | Limits | Best For |
|----------|-----|-------------|--------|----------|
| **OpenRouter** ⭐ | openrouter.ai | 18+ | None | Coding, 1M context |
| **Together AI** | api.together.xyz | 5+ | $5 credits | Multi-purpose |
| **Groq** | console.groq.com | 4+ | High limits | Fast inference |
| **Cohere** | dashboard.cohere.com | 3+ | Trial | Command-R series |
| **HuggingFace** | huggingface.co | 10+ | Rate limited | Specialized |
| **Cloudflare** | dash.cloudflare.com | 5+ | 10K/day | Edge inference |
| **Lepton AI** | lepton.ai | 3+ | Free compute | Llama, Mixtral |
| **Mistral** | mistral.ai | 2+ | Free tier | French models |
| **Google AI** | aistudio.google.com | 3+ | Free | Gemini |
| **Perplexity** | perplexity.ai | 1+ | Trial | Search |
| **Replicate** | replicate.com | Various | Free tier | Open source |

**Total: 50+ completely free models**

### 2.2 Free Model Rankings

**By Coding Capability (Artificial Analysis):**

| Rank | Model | Provider | Score |
|------|-------|----------|-------|
| 1 | DeepSeek V4 Flash:free | OpenRouter | 39.8% |
| 2 | Qwen3 Coder 480B:free | OpenRouter | 24.6% |
| 3 | Llama 3.3 70B:free | OpenRouter | 10.7% |
| 4 | Gemma 4 31B:free | OpenRouter | ? |

**By Agentic Capability:**

| Rank | Model | Provider | Score |
|------|-------|----------|-------|
| 1 | DeepSeek V4 Flash:free | OpenRouter | 62.3% |
| 2 | Qwen3 Coder 480B:free | OpenRouter | 18.3% |
| 3 | Llama 3.3 70B:free | OpenRouter | 9.1% |

---

## 3. TASK-TO-MODEL ASSIGNMENT

### 3.1 Routing Strategy

```
TASK TYPE                    PRIMARY MODEL              FALLBACK
─────────────────────────────────────────────────────────────────────
SWE-bench Generation         deepseek/deepseek-v4-flash:free    qwen/qwen3-coder:free
Deep Reasoning              deepseek/deepseek-v4-flash:free    llama-3.3-70b-versatile
Bug Detection              qwen/qwen3-coder:free          llama-3.1-8b-instant
Code Review               llama-3.3-70b-instruct:free    deepseek-v4-flash:free
Test Writing             qwen/qwen3-coder:free          together/qwen-32b
Fast Response            llama-3.1-8b-instant (Groq)    llama-3.1-8b-instant:free
Long Context            deepseek-v4-flash:free (1M!)    qwen/qwen3-coder:free
Agent Swarm Subtask     deepseek-v4-flash:free          any-free-model
```

---

## 4. KEY TECHNIQUES TO IMPLEMENT

### 4.1 From Kimi K2.5

**Agent Swarm Pattern:**
```
1. Main agent: "Decompose this task into sub-tasks"
2. For each sub-task:
   - Spawn parallel sub-agent
   - Each works independently
   - Return results
3. Main agent: "Synthesize results into final solution"
```

**Context Management:**
```
1. Set threshold (e.g., 200K tokens)
2. When exceeded:
   - Keep latest tool messages
   - Keep system prompt
   - Prune old user/assistant messages
   - Retain relevant context
```

### 4.2 From Claude Code

**Test-First Loop:**
```
1. Read test file FIRST
2. Understand what it expects
3. Write code to pass test
4. Run tests
5. Fix until pass
```

**Iterative Refinement:**
```
while not success:
   observe()
   if failure:
       debug()
       fix()
   verify()
```

### 4.3 From SWE-agent

**Minimal Tool Set:**
- bash tool
- create_file, insert_file
- view tool (read)
- str_replace tool (precise edit)
- submit tool

---

## 5. NEURO IMPLEMENTATION ROADMAP

### Phase 1: Core (Completed)
- [x] Smart Router ✅
- [x] Chain-of-thought ✅
- [x] Multi-pass thinking ✅
- [x] Test validation ✅
- [x] Patch guards ✅
- [x] Memory system ✅

### Phase 2: Advanced (In Progress)
- [x] Agent Swarm orchestration
- [x] Tool-enhanced reasoning
- [x] Context compression
- [ ] Web search (SearXNG)
- [ ] Parallel model execution

### Phase 3: Future
- [ ] Kimi K2.5 integration (open source!)
- [ ] Distributed execution
- [ ] Vision input
- [ ] Custom fine-tuning

---

## 6. TARGET METRICS

| Benchmark | Kimi K2.5 | Neuro Target | Neuro Min |
|-----------|-----------|--------------|-----------|
| SWE-bench Verified | 76.8% | 75% | 65% |
| SWE-bench Multilingual | 73.0% | 70% | 60% |
| Terminal Bench | 50.8% | 50% | 40% |
| Agent Swarm | 78.4% | 60% | 50% |
| LiveCodeBench | 85.0% | 75% | 65% |

**Realistic Target: 65-75%** (5 runs averaged)
**Aggressive Target: 75-80%** (with optimization)

---

## 7. COMPETITIVE ADVANTAGES

### What We Have That Paid Models Don't:

1. **Multi-Provider Routing** - Use ALL free models, not just one
2. **Graceful Degradation** - Fallback when provider fails
3. **Task History** - Learn from past failures (SQLite)
4. **Open-Source** - Full control, no vendor lock-in
5. **Customizable** - Modify architecture as needed
6. **Cost Tracking** - Monitor across providers

### How to Compete Without Paid APIs:

**Strategy 1: Ensemble + Smart Routing**
- Best model per task type
- Multiple models for hard tasks
- Fallback chain ensures completion
- 5 runs averaged = higher success rate

**Strategy 2: Architecture > Raw Power**
- Kimi uses architecture to get 76.8%
- We replicate architecture with free models
- Better prompts + validation = similar results
- Multi-pass compensates for weaker models

**Strategy 3: Better Context Management**
- Compress context to fit more info
- Prioritize recent/relevant context
- Same effective context as 1M models
- Discard strategy from Kimi

---

## 8. REFERENCES

1. **Kimi K2.5:** https://github.com/MoonshotAI/Kimi-K2.5
2. **SWE-bench:** https://arxiv.org/abs/2310.17567
3. **SWE-agent:** https://github.com/princeton-nlp/SWE-agent
4. **OpenRouter:** https://openrouter.ai/models?price=free
5. **Together AI:** https://api.together.xyz
6. **Manus AI:** https://manus.im
7. **Claude Code:** https://docs.anthropic.com/claude-code

---

## 9. OPEN SOURCE MODELS TO INTEGRATE

### Kimi K2.5 (Open Source!)
- Download: `huggingface.co/moonshotai/Kimi-K2.5`
- 1T params (requires significant compute)
- Can run locally with good GPU
- Alternative: API access via Moonshot

### Other Open Source SWE-bench Models:
- SWE-agent models
- BigCode models
- Qwen Coder models
- DeepSeek Coder models

---

**End of Research Document**
