# Neuro - Autonomous Coding System

An intelligent multi-model routing agent system with automatic skill integration.

## Features

- **Smart Router**: Routes tasks to 50+ free AI models based on task type
- **Chain-of-Thought Reasoning**: Multi-pass thinking with error correction
- **Patch Guards**: Only applies verified, non-breaking changes
- **Memory System**: Learns from past failures
- **Automatic Skill Integration**: 40+ built-in skills that auto-trigger based on context

## Available Skills

The system includes automatic integration for 40+ skills:

| Category | Skills |
|----------|--------|
| **Version Control** | github, gitlab, bitbucket, github-pr-review, iterate |
| **Code Quality** | code-review, code-simplifier, add-javadoc, security |
| **Frontend** | frontend-design, theme-factory |
| **DevOps** | docker, kubernetes, ssh, vercel, azure-devops |
| **Data/ML** | jupyter, spark-version-upgrade, datadog |
| **Communication** | slack-channel-monitor, discord, notion, linear |
| **Agent SDK** | openhands-sdk, agent-sdk-builder, agent-creator |
| **Meta** | add-skill, agent-memory, skill-creator, release-notes |

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
```

## Automatic Skill Triggering

Skills are automatically triggered based on:
- Task keywords (e.g., "github", "security", "frontend")
- File types (e.g., .py → code-review, .tsx → frontend-design)
- Error context (e.g., security errors → security skill)
- Code patterns (regex-based matching)

## License

MIT
