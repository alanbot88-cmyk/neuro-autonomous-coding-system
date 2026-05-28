# Neuro - Autonomous Coding System

An intelligent multi-model routing agent system with automatic skill integration.

## Features

- **Smart Router**: Routes tasks to 50+ free AI models based on task type
- **Chain-of-Thought Reasoning**: Multi-pass thinking with error correction
- **Patch Guards**: Only applies verified, non-breaking changes
- **Memory System**: Learns from past failures
- **Automatic Skill Integration**: 259+ skills + 15+ plugins auto-triggered based on context

## Available Skills & Plugins

### Core Skills (259+)
| Category | Skills |
|----------|--------|
| **Version Control** | github, gitlab, bitbucket, github-pr-review, iterate, ssh |
| **Code Quality** | code-review, code-simplifier, add-javadoc, security |
| **Frontend** | frontend-design, theme-factory |
| **DevOps** | docker, kubernetes, ssh, vercel, azure-devops |
| **Data/ML** | jupyter, spark-version-upgrade, datadog, tensorflow, pytorch |
| **Communication** | slack-channel-monitor, discord, notion, linear |
| **Agent SDK** | openhands-sdk, agent-sdk-builder, agent-creator |
| **Meta** | add-skill, agent-memory, skill-creator, release-notes |

### New Skills Added (4)
| Skill | Description |
|-------|-------------|
| **MCP Integration (swarmclaw)** | Model Context Protocol integration for connecting to Ollama, LM Studio, OpenAI, Anthropic |
| **Open Design Skills** | Access to 259+ OpenHands skills catalog with category-based lookup |
| **Agent Memory (swarmvault)** | Persistent memory system for learning from experience |
| **Browser Automation** | Playwright-based web automation and scraping |

### Plugins (10+)
| Plugin | Purpose |
|--------|---------|
| city-weather | Weather API integration |
| cobol-modernization | Legacy COBOL code modernization |
| magic-test | Intelligent test generation |
| migration-scoring | Migration analysis and scoring |
| onboarding | Project onboarding assistance |
| openhands | OpenHands integration |
| pr-review | Automated PR review |
| qa-changes | QA testing automation |
| release-notes | Changelog generation |
| vulnerability-remediation | Security vulnerability fixes |

## Usage

```python
from neuro import create_agent

# Create an agent
agent = create_agent(goal="Fix the security vulnerability in auth.py")
result = agent.run()

# Auto-skill detection
from neuro.skills import auto_skills

# Skills are automatically invoked based on task context
result = auto_skills("Review PR changes", {"file_path": "src/main.py"})

# Invoke specific skills
from neuro.skills import invoke_skill, mcp_connect, browse_web, store_memory

# MCP Integration
mcp_result = mcp_connect(provider="ollama", model="llama2")

# Browser Automation
browse_result = browse_web("Navigate to https://example.com and click the login button")

# Memory System
store_memory("Learned to use the new API pattern", tags=["api", "pattern"])
```

## Automatic Skill Triggering

Skills are automatically triggered based on:
- Task keywords (e.g., "github", "security", "frontend", "mcp", "browser")
- File types (e.g., .py → code-review, .tsx → frontend-design)
- Error context (e.g., security errors → security skill)
- Code patterns (regex-based matching)

## New Skill Usage Examples

### MCP Integration (swarmclaw)
```python
from neuro.skills import MCPSkill, mcp_invoke

# Connect to Ollama
result = mcp_invoke("Process this task", provider="ollama", model="llama2")

# Connect to LM Studio
result = mcp_invoke("Analyze code", provider="lm_studio", endpoint="http://localhost:1234")
```

### Browser Automation (Playwright)
```python
from neuro.skills import BrowserAutomation

# Natural language task
result = BrowserAutomation.invoke(
    "Navigate to github.com and click on the Sign In button"
)

# Get generated script
print(result["playwright_script"])
```

### Agent Memory (swarmvault)
```python
from neuro.skills import remember, recall, get_context, MemoryType

# Store important information
remember("Fixed the auth bug by updating the token validation", 
         memory_type=MemoryType.EPISODIC,
         tags=["bug-fix", "auth"])

# Recall relevant memories
memories = recall("auth bug fix")

# Get context for a new task
context = get_context("Fix login issue")
```

## License

MIT
