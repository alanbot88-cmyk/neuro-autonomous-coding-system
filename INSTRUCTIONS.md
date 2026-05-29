
---

## NEW FEATURES (v0.3.0 - 10 Section Agent Build)

### Role-Based Agent Swarm
The agent now uses 5 specialized roles:
- ManagerAgent: Task decomposition, specialist assignment
- ResearcherAgent: Codebase search, context building
- EngineerAgent: Test-first, small-chunk code writing
- ValidatorAgent: Test execution, confidence scoring
- ReviewerAgent: Final completeness check

Run with --verbose to see all roles in action.

### Scenario Routing (12 Handlers)
Auto-detects task type and applies specialized handling:

| Scenario | Approach | Threshold |
|----------|----------|-----------|
| bug_fix | diagnose - fix - verify | 0.85 |
| new_feature | plan - implement - test | 0.80 |
| refactor | analyze - plan - execute - verify | 0.90 |
| web_app | design - backend - frontend - integrate - test | 0.75 |
| api_build | schema - endpoints - validation - tests - docs | 0.85 |
| data_pipeline | validate - transform - validate - test | 0.85 |
| code_review | analyze - identify - suggest | 0.80 |
| research_task | gather - analyze - summarize | 0.70 |
| long_horizon | milestone - track - iterate | 0.80 |
| enterprise_app | architecture - design - implement - test - deploy | 0.80 |
| mobile_app | design - implement - test - package | 0.75 |
| presentation | outline - design - build - refine | 0.75 |

Usage:
  python -m neuro --scenario api_build --goal "Create user API"
  python -m neuro --goal "Fix the login bug"  # auto-detects bug_fix

### Confidence Threshold System
- Agent won't stop until confidence >= threshold
- Test results trigger automatic retry if below threshold
- Thresholds: code_fix=0.85, new_feature=0.80, refactor=0.90, web_app=0.75

### Purpose-Built Coding Tools (ACI)
14 specialized tools for coding tasks:
- view_file, search_dir, search_symbol, find_tests
- get_function, get_class, apply_diff, create_file
- run_tests, get_git_context, detect_language
- get_imports, find_similar_code

### Smart Context Engine
- Automatically builds surgical context bundles
- Summarizes old conversation turns
- Ranks code snippets by relevance
- Detects scope of files/modules

### Persistence Engine (Never Give Up)
- Agent tries alternative approaches when stuck
- Rechecks goal every 5 steps to prevent drift
- Handles blockers with multiple strategies
- MAX_ALTERNATIVE_APPROACHES = 3

### Parallel Execution
- Independent subtasks run in parallel
- Respects rate limits (20 req/min per provider)
- Distributes across providers
- Use --no-parallel to disable

### Memory & Learning
- System learns from past failures
- Tracks per-model performance
- Suggests best model for task type
- Data stored in ~/.neuro/task_history.db

---

**Last Updated: 2026-05-29**
**Version: 0.3.0**
**Features: 50+ FREE API Models, 5-Role Agent Swarm, 12 Scenario Handlers, Confidence Thresholds, ACI Tools, Smart Context, Persistence, Parallel Execution, Memory Learning**
