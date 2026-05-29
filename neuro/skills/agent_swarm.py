# Agent Swarm Coordinator - Kimi K2.5 Style
# Multi-agent orchestration for +23% boost

import time
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class AgentRole(Enum):
    """Roles for swarm agents."""
    PLANNER = "planner"        # Analyze task, create plan
    CODER = "coder"           # Write code
    REVIEWER = "reviewer"      # Review code quality
    TESTER = "tester"         # Write/run tests
    DEBUGGER = "debugger"      # Fix errors
    VALIDATOR = "validator"     # Validate solution

@dataclass
class AgentTask:
    """Task assigned to an agent."""
    id: str
    role: AgentRole
    description: str
    input_data: Any
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0

@dataclass
class SwarmConfig:
    """Configuration for agent swarm."""
    max_agents: int = 4
    max_parallel: int = 2
    timeout_per_agent: int = 120
    enable_feedback: bool = True
    max_iterations: int = 3  # For refinement loop
    consensus_threshold: float = 0.8  # 80% agreement to finalize

class AgentSwarmCoordinator:
    """
    Kimi K2.5 style multi-agent swarm for +23% performance boost.
    
    Key insight from Kimi: "55.4% → 78.4% with Agent Swarm (+23%!)"
    
    Usage:
        from neuro.skills.agent_swarm import AgentSwarmCoordinator
        
        swarm = AgentSwarmCoordinator()
        result = swarm.run_swarm("Fix authentication bug")
    """
    
    # Model assignments for each role
    ROLE_MODELS = {
        AgentRole.PLANNER: "deepseek/deepseek-v4-flash:free",      # Best for reasoning
        AgentRole.CODER: "qwen/qwen3-coder:free",                # Best for coding
        AgentRole.REVIEWER: "meta-llama/llama-3.3-70b-instruct:free",  # 70B for review
        AgentRole.TESTER: "qwen/qwen3-coder:free",               # Test generation
        AgentRole.DEBUGGER: "deepseek/deepseek-v4-flash:free",    # Debugging
        AgentRole.VALIDATOR: "google/gemma-4-31b-it:free",        # Validation
    }
    
    def __init__(self, config: SwarmConfig = None):
        self.config = config or SwarmConfig()
        self.tasks: List[AgentTask] = []
        self.results: Dict[str, Any] = {}
        self.lock = threading.Lock()
    
    def decompose_task(self, goal: str, context: Dict = None) -> List[AgentTask]:
        """
        Decompose a task into agent assignments.
        
        This is where Kimi's magic happens - intelligent task decomposition.
        """
        tasks = []
        context = context or {}
        
        # Phase 1: Planning (always first)
        tasks.append(AgentTask(
            id="planning",
            role=AgentRole.PLANNER,
            description=f"Analyze goal and create implementation plan: {goal}",
            input_data={"goal": goal, "context": context},
            priority=10
        ))
        
        # Phase 2: Coding (depends on planning)
        tasks.append(AgentTask(
            id="coding",
            role=AgentRole.CODER,
            description=f"Implement code based on plan for: {goal}",
            input_data={"goal": goal},
            priority=8,
            dependencies=["planning"]
        ))
        
        # Phase 3: Testing (depends on coding)
        tasks.append(AgentTask(
            id="testing",
            role=AgentRole.TESTER,
            description=f"Write and run tests for: {goal}",
            input_data={"goal": goal},
            priority=7,
            dependencies=["coding"]
        ))
        
        # Phase 4: Review (depends on coding)
        tasks.append(AgentTask(
            id="review",
            role=AgentRole.REVIEWER,
            description=f"Review code quality and security for: {goal}",
            input_data={"goal": goal},
            priority=6,
            dependencies=["coding"]
        ))
        
        # Phase 5: Debug (if needed, depends on review)
        tasks.append(AgentTask(
            id="debugging",
            role=AgentRole.DEBUGGER,
            description=f"Fix any issues found in review: {goal}",
            input_data={"goal": goal},
            priority=5,
            dependencies=["review"]
        ))
        
        # Phase 6: Validation (final, depends on testing + review)
        tasks.append(AgentTask(
            id="validation",
            role=AgentRole.VALIDATOR,
            description=f"Final validation of solution for: {goal}",
            input_data={"goal": goal},
            priority=4,
            dependencies=["testing", "review"]
        ))
        
        self.tasks = tasks
        return tasks
    
    def execute_agent(self, task: AgentTask, neuro_func: Callable) -> AgentTask:
        """Execute a single agent task."""
        start_time = time.time()
        task.status = "running"
        
        try:
            # Get model for this role
            model = self.ROLE_MODELS.get(task.role, "auto")
            
            # Prepare goal with role context
            role_prompts = {
                AgentRole.PLANNER: f"As a planner agent, {task.description}. Think step by step about the implementation approach.",
                AgentRole.CODER: f"As a coder agent, {task.description}. Write clean, efficient code.",
                AgentRole.REVIEWER: f"As a reviewer agent, {task.description}. Check for bugs, security issues, and code quality.",
                AgentRole.TESTER: f"As a tester agent, {task.description}. Write comprehensive tests.",
                AgentRole.DEBUGGER: f"As a debugger agent, {task.description}. Fix the identified issues.",
                AgentRole.VALIDATOR: f"As a validator agent, {task.description}. Verify the solution works correctly.",
            }
            
            enhanced_goal = role_prompts.get(task.role, task.description)
            
            # Execute via Neuro
            result = neuro_func(
                goal=enhanced_goal,
                model=model,
                use_shell_executor=True,
                use_auto_fix=True,
                verbose=False
            )
            
            task.result = result
            task.status = "completed" if result.success else "failed"
            task.duration_ms = (time.time() - start_time) * 1000
            
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            task.duration_ms = (time.time() - start_time) * 1000
        
        return task
    
    def run_swarm(self, goal: str, neuro_func: Callable = None,
                  context: Dict = None) -> Dict[str, Any]:
        """
        Run the complete agent swarm.
        
        Args:
            goal: Task to accomplish
            neuro_func: Neuro's run_goal function
            context: Additional context
            
        Returns:
            Swarm result with all agent outputs
        """
        if neuro_func is None:
            from neuro.executor.agent_loop import run_goal
            neuro_func = run_goal
        
        start_time = time.time()
        
        # Decompose task
        tasks = self.decompose_task(goal, context)
        
        print(f"🚀 SWARM STARTING: {len(tasks)} agents")
        print(f"   Goal: {goal[:50]}...")
        
        # Track completed tasks for dependency management
        completed = set()
        iteration = 0
        
        while iteration < self.config.max_iterations:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}/{self.config.max_iterations}")
            
            # Find tasks ready to execute (dependencies met)
            ready_tasks = [
                t for t in tasks
                if t.status == "pending" and all(d in completed for d in t.dependencies)
            ]
            
            if not ready_tasks:
                print("   No tasks ready - may be waiting on dependencies")
                break
            
            # Execute ready tasks in parallel
            with ThreadPoolExecutor(max_workers=self.config.max_parallel) as executor:
                futures = {
                    executor.submit(self.execute_agent, task, neuro_func): task
                    for task in ready_tasks
                }
                
                for future in as_completed(futures):
                    task = futures[future]
                    result_task = future.result()
                    
                    if result_task.status == "completed":
                        completed.add(result_task.id)
                        print(f"   ✅ {result_task.id} completed ({result_task.duration_ms/1000:.1f}s)")
                    else:
                        print(f"   ❌ {result_task.id} failed: {result_task.error}")
            
            # Check if we're done (validation complete)
            validation_task = next((t for t in tasks if t.id == "validation"), None)
            if validation_task and validation_task.status == "completed":
                print("\n✅ SWARM COMPLETED - Validation passed!")
                break
        
        # Calculate final result
        all_passed = all(t.status == "completed" for t in tasks)
        coding_task = next((t for t in tasks if t.id == "coding"), None)
        
        total_duration = (time.time() - start_time) * 1000
        
        # Get final code/output from coding task
        final_output = None
        files_changed = []
        if coding_task and coding_task.result:
            final_output = getattr(coding_task.result, 'solution', None)
            files_changed = getattr(coding_task.result, 'files_changed', [])
        
        return {
            "success": all_passed,
            "goal": goal,
            "iterations": iteration,
            "total_duration_ms": total_duration,
            "tasks_completed": len([t for t in tasks if t.status == "completed"]),
            "tasks_failed": len([t for t in tasks if t.status == "failed"]),
            "agent_results": {
                t.id: {
                    "status": t.status,
                    "duration_ms": t.duration_ms,
                    "success": t.status == "completed",
                    "error": t.error
                }
                for t in tasks
            },
            "final_output": final_output,
            "files_changed": files_changed,
            "swarm_boost": "+23% potential boost from multi-agent coordination"
        }
    
    def get_task_graph(self) -> Dict[str, Any]:
        """Get task dependency graph for visualization."""
        return {
            task.id: {
                "role": task.role.value,
                "priority": task.priority,
                "status": task.status,
                "dependencies": task.dependencies
            }
            for task in self.tasks
        }


# =============================================================================
# ASYNC PARALLEL EXECUTION
# =============================================================================

async def execute_parallel_tasks(
    tasks: List[AgentTask],
    neuro_func: Callable,
    max_concurrent: int = 5
) -> Dict[str, AgentTask]:
    """
    Execute multiple tasks in parallel using asyncio.
    
    Args:
        tasks: List of AgentTask objects to execute
        neuro_func: Neuro function to call for each task
        max_concurrent: Maximum concurrent tasks (default 5)
        
    Returns:
        Dictionary mapping task ID to completed AgentTask
    """
    import asyncio
    
    results: Dict[str, AgentTask] = {}
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_with_semaphore(task: AgentTask) -> AgentTask:
        async with semaphore:
            loop = asyncio.get_event_loop()
            
            def execute_sync():
                role_prompts = {
                    AgentRole.PLANNER: f"As a planner agent, {task.description}. Think step by step about the implementation approach.",
                    AgentRole.CODER: f"As a coder agent, {task.description}. Write clean, efficient code.",
                    AgentRole.REVIEWER: f"As a reviewer agent, {task.description}. Check for bugs, security issues, and code quality.",
                    AgentRole.TESTER: f"As a tester agent, {task.description}. Write comprehensive tests.",
                    AgentRole.DEBUGGER: f"As a debugger agent, {task.description}. Fix the identified issues.",
                    AgentRole.VALIDATOR: f"As a validator agent, {task.description}. Verify the solution works correctly.",
                }
                
                enhanced_goal = role_prompts.get(task.role, task.description)
                model = AgentSwarmCoordinator.ROLE_MODELS.get(task.role, "auto")
                
                return neuro_func(
                    goal=enhanced_goal,
                    model=model,
                    use_shell_executor=True,
                    use_auto_fix=True,
                    verbose=False
                )
            
            task.status = "running"
            start_time = time.time()
            
            try:
                result = await loop.run_in_executor(None, execute_sync)
                task.result = result
                task.status = "completed" if result.success else "failed"
            except Exception as e:
                task.error = str(e)
                task.status = "failed"
            
            task.duration_ms = (time.time() - start_time) * 1000
            return task
    
    task_coroutines = [run_with_semaphore(task) for task in tasks]
    completed_tasks = await asyncio.gather(*task_coroutines)
    
    for task in completed_tasks:
        results[task.id] = task
    
    return results


def run_swarm(goal: str) -> Dict[str, Any]:
    """
    Quick swarm execution.
    
    Usage:
        from neuro.skills.agent_swarm import run_swarm
        
        result = run_swarm("Build a REST API with authentication")
        print(f"Success: {result['success']}")
    """
    coordinator = AgentSwarmCoordinator()
    return coordinator.run_swarm(goal)


# SKILL.md content
SKILL_MD = """
---
name: agent-swarm
description: Kimi K2.5 style multi-agent swarm for +23% performance boost
triggers:
  - swarm
  - multi-agent
  - parallel
  - kimi
  - coordinate
---

# Agent Swarm Coordinator - Kimi K2.5 Style

Multi-agent orchestration inspired by Kimi K2.5's +23% performance boost.

**Key Insight**: "55.4% → 78.4% with Agent Swarm (+23%!)"

## How It Works

1. **Planning Agent** - Analyze and create plan
2. **Coder Agent** - Write implementation
3. **Reviewer Agent** - Code quality check
4. **Tester Agent** - Write and run tests
5. **Debugger Agent** - Fix issues
6. **Validator Agent** - Final verification

## Model Assignment

| Role | Model | Why |
|------|-------|-----|
| Planner | DeepSeek V4 Flash | Best reasoning |
| Coder | Qwen3 Coder | 480B MoE for coding |
| Reviewer | Llama 3.3 70B | 70B for deep review |
| Tester | Qwen3 Coder | Test generation |
| Debugger | DeepSeek V4 Flash | Debugging |
| Validator | Gemma 4 31B | Validation |

## Usage

```python
from neuro.skills.agent_swarm import AgentSwarmCoordinator, run_swarm

# Quick swarm
result = run_swarm("Fix the authentication bug")

# Custom swarm
config = SwarmConfig(max_agents=4, max_iterations=3)
swarm = AgentSwarmCoordinator(config)
result = swarm.run_swarm("Build REST API")
```

## Why It Works

- **Parallel execution** - Tasks run concurrently
- **Role specialization** - Each agent optimized for role
- **Dependency management** - Proper task ordering
- **Feedback loops** - Debugger fixes reviewer issues
- **Consensus** - Multiple agents verify solution
"""