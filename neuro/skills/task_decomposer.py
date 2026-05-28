# Task Decomposition Planner
# Inspired by ECC's /plan command
# Creates detailed implementation plans from high-level goals

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class TaskSize(Enum):
    XS = "xs"  # < 15 min
    S = "s"    # 15-30 min
    M = "m"    # 30-60 min
    L = "l"    # 60-120 min
    XL = "xl"  # > 120 min

@dataclass
class TaskStep:
    """A single step in the implementation plan."""
    id: str
    description: str
    action: str  # "code", "test", "review", "deploy", "config"
    size: TaskSize = TaskSize.M
    dependencies: List[str] = field(default_factory=list)
    estimated_minutes: int = 30
    model_hint: Optional[str] = None  # Which model to use
    acceptance_criteria: List[str] = field(default_factory=list)
    notes: Optional[str] = None

@dataclass
class ImplementationPlan:
    """Complete implementation plan."""
    title: str
    goal: str
    steps: List[TaskStep]
    total_estimated_minutes: int = 0
    parallel_possible: List[Tuple[str, str]] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    context_needed: List[str] = field(default_factory=list)

class TaskDecomposer:
    """
    Task decomposition planner inspired by ECC's /plan command.
    Creates detailed, executable plans from high-level goals.
    
    Usage:
        from neuro.skills.task_decomposer import TaskDecomposer, create_plan
        
        decomposer = TaskDecomposer()
        plan = decomposer.decompose("Add user authentication to the API")
    """
    
    ACTION_PATTERNS = {
        "code": [
            "implement", "add", "create", "build", "write", "develop",
            "modify", "update", "fix", "change", "refactor"
        ],
        "test": [
            "test", "spec", "verify", "check", "validate", "ensure"
        ],
        "review": [
            "review", "audit", "inspect", "analyze", "assess"
        ],
        "config": [
            "configure", "setup", "install", "enable", "add config"
        ],
        "deploy": [
            "deploy", "release", "publish", "ship", "launch"
        ],
        "research": [
            "research", "investigate", "explore", "find", "lookup"
        ]
    }
    
    SIZE_ESTIMATES = {
        "xs": 5,
        "s": 15,
        "m": 30,
        "l": 60,
        "xl": 120
    }
    
    def __init__(self):
        self.plans: List[ImplementationPlan] = []
    
    def decompose(self, goal: str, context: Dict[str, Any] = None) -> ImplementationPlan:
        """
        Decompose a goal into detailed implementation steps.
        
        Args:
            goal: High-level goal description
            context: Additional context (language, framework, etc.)
            
        Returns:
            ImplementationPlan with detailed steps
        """
        context = context or {}
        goal_lower = goal.lower()
        
        # Detect task type and language
        language = self._detect_language(goal_lower, context)
        task_type = self._detect_task_type(goal_lower)
        
        # Generate steps
        steps = self._generate_steps(goal, language, task_type)
        
        # Calculate totals
        total_minutes = sum(s.estimated_minutes for s in steps)
        
        # Identify parallel possibilities
        parallel = self._find_parallel_steps(steps)
        
        # Identify risks
        risks = self._identify_risks(goal, steps)
        
        # Context needed
        context_needed = self._identify_context(goal, steps)
        
        plan = ImplementationPlan(
            title=self._generate_title(goal),
            goal=goal,
            steps=steps,
            total_estimated_minutes=total_minutes,
            parallel_possible=parallel,
            risks=risks,
            context_needed=context_needed
        )
        
        self.plans.append(plan)
        return plan
    
    def _detect_language(self, goal_lower: str, context: Dict) -> str:
        """Detect programming language from goal and context."""
        language_map = {
            "python": ["python", "django", "flask", "fastapi", ".py"],
            "javascript": ["javascript", "node", "react", "vue", ".js", "typescript", ".ts"],
            "go": ["golang", "go ", "go.", "microservice"],
            "java": ["java", "spring", "maven", ".java"],
            "rust": ["rust", "cargo", ".rs"],
            "cpp": ["c++", "cpp", ".cpp", ".hpp"],
            "csharp": ["csharp", "c#", ".cs", ".net"],
        }
        
        for lang, keywords in language_map.items():
            if any(kw in goal_lower for kw in keywords):
                return lang
            if context.get("language", "").lower() == lang:
                return lang
        
        return context.get("language", "general")
    
    def _detect_task_type(self, goal_lower: str) -> str:
        """Detect the type of task."""
        if any(k in goal_lower for k in ["auth", "login", "user", "session"]):
            return "authentication"
        elif any(k in goal_lower for k in ["api", "endpoint", "rest", "graphql"]):
            return "api"
        elif any(k in goal_lower for k in ["database", "db", "sql", "migrate"]):
            return "database"
        elif any(k in goal_lower for k in ["test", "spec"]):
            return "testing"
        elif any(k in goal_lower for k in ["security", "vulnerability", "audit"]):
            return "security"
        elif any(k in goal_lower for k in ["deploy", "ci", "cd", "docker"]):
            return "deployment"
        else:
            return "feature"
    
    def _generate_steps(self, goal: str, language: str, task_type: str) -> List[TaskStep]:
        """Generate implementation steps based on goal type."""
        steps = []
        step_counter = 1
        
        # Research/discovery step (almost always needed)
        steps.append(TaskStep(
            id=f"step_{step_counter}",
            description=f"Research existing {language} codebase structure and patterns",
            action="research",
            size=TaskSize.XS,
            estimated_minutes=10,
            notes="Understand existing code organization"
        ))
        step_counter += 1
        
        # Task-specific steps
        if task_type == "authentication":
            steps.extend([
                TaskStep(
                    id=f"step_{step_counter}",
                    description="Design authentication flow (login, logout, session management)",
                    action="code",
                    size=TaskSize.M,
                    estimated_minutes=45,
                    model_hint="planner",
                    dependencies=[f"step_{step_counter-1}"]
                ),
                TaskStep(
                    id=f"step_{step_counter+1}",
                    description="Write authentication tests",
                    action="test",
                    size=TaskSize.S,
                    estimated_minutes=20,
                    model_hint="tester",
                    dependencies=[f"step_{step_counter}"]
                ),
                TaskStep(
                    id=f"step_{step_counter+2}",
                    description="Security review of auth implementation",
                    action="review",
                    size=TaskSize.S,
                    estimated_minutes=20,
                    model_hint="security_reviewer",
                    dependencies=[f"step_{step_counter+1}"]
                ),
            ])
            step_counter += 3
        
        elif task_type == "api":
            steps.extend([
                TaskStep(
                    id=f"step_{step_counter}",
                    description="Define API schema and endpoints",
                    action="config",
                    size=TaskSize.M,
                    estimated_minutes=30,
                    model_hint="architect"
                ),
                TaskStep(
                    id=f"step_{step_counter+1}",
                    description="Implement API handlers",
                    action="code",
                    size=TaskSize.M,
                    estimated_minutes=60,
                    model_hint="code_generator",
                    dependencies=[f"step_{step_counter}"]
                ),
                TaskStep(
                    id=f"step_{step_counter+2}",
                    description="Add API tests",
                    action="test",
                    size=TaskSize.S,
                    estimated_minutes=30,
                    model_hint="tester",
                    dependencies=[f"step_{step_counter+1}"]
                ),
                TaskStep(
                    id=f"step_{step_counter+3}",
                    description="Create API documentation",
                    action="code",
                    size=TaskSize.XS,
                    estimated_minutes=15,
                    dependencies=[f"step_{step_counter+2}"]
                ),
            ])
            step_counter += 4

        elif task_type == "database":
            steps.extend([
                TaskStep(
                    id=f"step_{step_counter}",
                    description="Design database schema",
                    action="config",
                    size=TaskSize.S,
                    estimated_minutes=25,
                    model_hint="architect"
                ),
                TaskStep(
                    id=f"step_{step_counter+1}",
                    description="Create migrations",
                    action="code",
                    size=TaskSize.S,
                    estimated_minutes=30,
                    model_hint="code_generator",
                    dependencies=[f"step_{step_counter}"]
                ),
                TaskStep(
                    id=f"step_{step_counter+2}",
                    description="Write database tests",
                    action="test",
                    size=TaskSize.S,
                    estimated_minutes=20,
                    model_hint="tester",
                    dependencies=[f"step_{step_counter+1}"]
                ),
            ])
            step_counter += 3

        else:  # General feature
            steps.extend([
                TaskStep(
                    id=f"step_{step_counter}",
                    description="Design solution architecture",
                    action="code",
                    size=TaskSize.S,
                    estimated_minutes=30,
                    model_hint="architect"
                ),
                TaskStep(
                    id=f"step_{step_counter+1}",
                    description="Implement core functionality",
                    action="code",
                    size=TaskSize.M,
                    estimated_minutes=60,
                    model_hint="code_generator",
                    dependencies=[f"step_{step_counter}"]
                ),
                TaskStep(
                    id=f"step_{step_counter+2}",
                    description="Add tests",
                    action="test",
                    size=TaskSize.S,
                    estimated_minutes=30,
                    model_hint="tester",
                    dependencies=[f"step_{step_counter+1}"]
                ),
            ])
            step_counter += 3
        # Final verification step
        steps.append(TaskStep(
            id=f"step_{step_counter}",
            description="Final verification - run all tests and verify functionality",
            action="test",
            size=TaskSize.S,
            estimated_minutes=15,
            acceptance_criteria=["All tests pass", "Functionality verified"],
            notes="Last step before completion"
        ))
        
        return steps
    
    def _find_parallel_steps(self, steps: List[TaskStep]) -> List[Tuple[str, str]]:
        """Find steps that can be done in parallel."""
        parallel = []
        
        # Steps with no dependencies can be parallel
        no_deps = [s for s in steps if not s.dependencies]
        for i, s1 in enumerate(no_deps):
            for s2 in no_deps[i+1:]:
                if s1.size in [TaskSize.XS, TaskSize.S] and s2.size in [TaskSize.XS, TaskSize.S]:
                    parallel.append((s1.id, s2.id))
        
        return parallel[:5]  # Limit to top 5 parallel opportunities
    
    def _identify_risks(self, goal: str, steps: List[TaskStep]) -> List[str]:
        """Identify potential risks."""
        risks = []
        goal_lower = goal.lower()
        
        if "auth" in goal_lower or "security" in goal_lower:
            risks.append("Authentication security must be carefully reviewed")
        
        if any(s.size == TaskSize.XL for s in steps):
            risks.append("Large task detected - consider breaking into smaller chunks")
        
        if len(steps) > 10:
            risks.append("Complex task with many steps - prioritize core functionality")
        
        if any("database" in s.description.lower() for s in steps):
            risks.append("Database changes require careful migration planning")
        
        return risks
    
    def _identify_context(self, goal: str, steps: List[TaskStep]) -> List[str]:
        """Identify required context."""
        context = []
        goal_lower = goal.lower()
        
        if "auth" in goal_lower:
            context.append("Current auth implementation")
            context.append("Security requirements")
        
        if "api" in goal_lower:
            context.append("API schema design")
            context.append("Existing endpoints")
        
        context.append("Project structure")
        context.append("Test framework used")
        
        return list(set(context))  # Remove duplicates
    
    def _generate_title(self, goal: str) -> str:
        """Generate a title from the goal."""
        # Truncate and clean up
        words = goal.split()[:6]
        title = " ".join(words)
        if len(goal.split()) > 6:
            title += "..."
        return title


def create_plan(goal: str, context: Dict = None) -> Dict[str, Any]:
    """
    Quick plan creation function.
    
    Usage:
        from neuro.skills.task_decomposer import create_plan
        
        plan = create_plan("Add JWT authentication to REST API")
        
        # Access plan details
        print(f"Title: {plan['title']}")
        print(f"Steps: {len(plan['steps'])}")
        print(f"Estimated: {plan['total_estimated_minutes']} minutes")
    """
    decomposer = TaskDecomposer()
    plan = decomposer.decompose(goal, context)
    
    return {
        "title": plan.title,
        "goal": plan.goal,
        "steps": [
            {
                "id": s.id,
                "description": s.description,
                "action": s.action,
                "size": s.size.value,
                "minutes": s.estimated_minutes,
                "dependencies": s.dependencies,
                "model_hint": s.model_hint,
                "acceptance_criteria": s.acceptance_criteria
            }
            for s in plan.steps
        ],
        "total_minutes": plan.total_estimated_minutes,
        "parallel_opportunities": plan.parallel_possible,
        "risks": plan.risks,
        "context_needed": plan.context_needed
    }


# SKILL.md content
SKILL_MD = """
---
name: task-decomposer
description: Intelligent task decomposition and planning
triggers:
  - plan
  - decompose
  - steps
  - implementation
  - breakdown
---

# Task Decomposer Skill

Intelligent task decomposition inspired by ECC's /plan command.
Creates detailed, executable plans from high-level goals.

## Features

### 1. Smart Decomposition
Automatically breaks down tasks into:
- Research steps
- Implementation steps  
- Testing steps
- Review steps

### 2. Size Estimation
Estimates task size (XS to XL):
- XS: < 15 min
- S: 15-30 min
- M: 30-60 min
- L: 60-120 min
- XL: > 120 min

### 3. Dependency Analysis
Identifies which steps depend on others.

### 4. Model Hints
Recommends which Neuro model to use:
- planner → Architect/analysis
- code_generator → DeepSeek V4 Flash
- tester → Qwen3 Coder
- security_reviewer → Llama 3.3 70B

### 5. Risk Identification
Detects potential risks:
- Security concerns
- Large tasks
- Database changes

## Usage

```python
from neuro.skills.task_decomposer import TaskDecomposer, create_plan

# Quick plan
plan = create_plan("Add user authentication")
print(f"Estimated: {plan['total_minutes']} minutes")
for step in plan['steps']:
    print(f"  {step['id']}: {step['description']}")

# Custom decomposition
decomposer = TaskDecomposer()
plan = decomposer.decompose(
    goal="Build REST API with tests",
    context={"language": "python", "framework": "fastapi"}
)
```

## Task Types Detected

- authentication: User auth flows
- api: REST/GraphQL endpoints
- database: Schema and migrations
- testing: Test writing
- security: Security audits
- deployment: CI/CD and deployment

## Integration with Neuro

Use model hints to route to optimal models:
```python
step_model_map = {
    "planner": "deepseek/deepseek-v4-flash:free",  # Analysis
    "code_generator": "qwen/qwen3-coder:free",  # Coding
    "tester": "qwen/qwen3-coder:free",  # Test generation
    "security_reviewer": "meta-llama/llama-3.3-70b-instruct:free"  # 70B review
}
```
"""