# Multi-Agent Orchestration Skill
# Inspired by ECC's multi-plan, multi-execute, and PM2 commands
# Enhanced from your basic agent swarm

import os
import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from collections import defaultdict


# =============================================================================
# RATE LIMIT CONFIGURATION
# =============================================================================

class RateLimitConfig:
    """Configuration for API rate limits."""
    DEFAULT_LIMITS = {
        "gemini": 20,  # requests per minute
        "groq": 30,
        "openrouter": 20,
        "huggingface": 10,
    }
    
    def __init__(self, custom_limits: Dict[str, int] = None):
        self.limits = {**self.DEFAULT_LIMITS, **(custom_limits or {})}
        self._request_times: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.Lock()
    
    def can_make_request(self, provider: str, max_per_minute: int = None) -> bool:
        """Check if we can make a request without exceeding rate limit."""
        limit = max_per_minute or self.limits.get(provider, 20)
        
        with self._lock:
            now = time.time()
            # Remove requests older than 1 minute
            self._request_times[provider] = [
                t for t in self._request_times[provider]
                if now - t < 60
            ]
            
            return len(self._request_times[provider]) < limit
    
    def record_request(self, provider: str):
        """Record that a request was made."""
        with self._lock:
            self._request_times[provider].append(time.time())
    
    def wait_if_needed(self, provider: str, max_per_minute: int = None):
        """Wait if we're at the rate limit."""
        limit = max_per_minute or self.limits.get(provider, 20)
        
        with self._lock:
            now = time.time()
            # Remove old requests
            self._request_times[provider] = [
                t for t in self._request_times[provider]
                if now - t < 60
            ]
            
            count = len(self._request_times[provider])
            if count >= limit:
                # Calculate wait time
                oldest = self._request_times[provider][0]
                wait_time = 60 - (now - oldest)
                if wait_time > 0:
                    time.sleep(wait_time)


# Global rate limit config
_rate_limiter = RateLimitConfig()

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SubTask:
    """A subtask for parallel execution."""
    id: str
    description: str
    assigned_agent: str  # Which agent type handles this
    priority: int = 0  # Higher = more important
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    model_used: Optional[str] = None

@dataclass
class OrchestrationPlan:
    """Plan for multi-agent execution."""
    tasks: List[SubTask]
    parallel_groups: List[List[str]]  # Task IDs that can run in parallel
    execution_order: List[str]  # Overall execution order respecting dependencies
    estimated_duration_ms: float = 0

class MultiAgentOrchestrator:
    """
    Multi-agent orchestration system.
    Evolved from your basic agent swarm to full ECC-style orchestration.
    
    Usage:
        from neuro.skills.multi_agent import MultiAgentOrchestrator
        
        orchestrator = MultiAgentOrchestrator()
        plan = orchestrator.create_plan("Build a web app")
        results = orchestrator.execute(plan)
    """
    
    def __init__(self, max_parallel: int = 4, max_retries: int = 2):
        self.max_parallel = max_parallel
        self.max_retries = max_retries
        self.plans: List[OrchestrationPlan] = []
        self.execution_history: List[Dict] = []
    
    def create_plan(self, task: str, context: Dict[str, Any] = None) -> OrchestrationPlan:
        """
        Create an execution plan by decomposing the task.
        
        This uses your router's model intelligence to:
        1. Decompose task into subtasks
        2. Identify dependencies
        3. Group parallelizable tasks
        4. Assign appropriate agents/models
        """
        context = context or {}
        
        # Smart task decomposition
        subtasks = self._decompose_task(task, context)
        
        # Identify parallel groups (tasks with no dependencies)
        parallel_groups = self._identify_parallel_groups(subtasks)
        
        # Create execution order
        execution_order = self._create_execution_order(subtasks, parallel_groups)
        
        plan = OrchestrationPlan(
            tasks=subtasks,
            parallel_groups=parallel_groups,
            execution_order=execution_order,
            estimated_duration_ms=self._estimate_duration(subtasks)
        )
        
        self.plans.append(plan)
        return plan
    
    def _decompose_task(self, task: str, context: Dict) -> List[SubTask]:
        """Decompose task into subtasks using intelligence."""
        subtasks = []
        task_lower = task.lower()
        
        # Use context-aware decomposition
        if "build" in task_lower or "create" in task_lower:
            subtasks.append(SubTask(
                id="planning",
                description="Create implementation plan",
                assigned_agent="planner",
                priority=10,
                dependencies=[]
            ))
            subtasks.append(SubTask(
                id="architecture",
                description="Design system architecture",
                assigned_agent="architect",
                priority=9,
                dependencies=["planning"]
            ))
        
        if any(k in task_lower for k in ["api", "backend", "server"]):
            subtasks.append(SubTask(
                id="backend",
                description="Implement backend logic",
                assigned_agent="code_generator",
                priority=7,
                dependencies=["architecture"] if "architecture" in [t.id for t in subtasks] else ["planning"]
            ))
        
        if any(k in task_lower for k in ["frontend", "ui", "web", "react"]):
            subtasks.append(SubTask(
                id="frontend",
                description="Implement frontend",
                assigned_agent="frontend_dev",
                priority=7,
                dependencies=["architecture"] if "architecture" in [t.id for t in subtasks] else ["planning"]
            ))
        
        if any(k in task_lower for k in ["test", "testing"]):
            subtasks.append(SubTask(
                id="testing",
                description="Write and run tests",
                assigned_agent="tester",
                priority=6,
                dependencies=["backend", "frontend"]
            ))
        
        if any(k in task_lower for k in ["deploy", "docker", "ci"]):
            subtasks.append(SubTask(
                id="deployment",
                description="Setup deployment",
                assigned_agent="devops",
                priority=5,
                dependencies=["testing"]
            ))
        
        if any(k in task_lower for k in ["fix", "bug", "repair"]):
            subtasks.append(SubTask(
                id="debug",
                description="Debug and fix issue",
                assigned_agent="debugger",
                priority=10,
                dependencies=[]
            ))
            subtasks.append(SubTask(
                id="verify_fix",
                description="Verify the fix works",
                assigned_agent="reviewer",
                priority=9,
                dependencies=["debug"]
            ))
        
        if any(k in task_lower for k in ["review", "pr", "audit"]):
            subtasks.append(SubTask(
                id="code_review",
                description="Review code quality",
                assigned_agent="reviewer",
                priority=8,
                dependencies=[]
            ))
        
        # Default task if nothing matched
        if not subtasks:
            subtasks.append(SubTask(
                id="main_task",
                description=task,
                assigned_agent="general",
                priority=5,
                dependencies=[]
            ))
        
        return subtasks
    
    def _identify_parallel_groups(self, tasks: List[SubTask]) -> List[List[str]]:
        """Identify which tasks can run in parallel."""
        # Build dependency map
        dep_map = {t.id: set(t.dependencies) for t in tasks}
        
        groups = []
        remaining = set(t.id for t in tasks)
        
        while remaining:
            # Find tasks with no remaining dependencies
            ready = [
                tid for tid in remaining
                if all(dep in (set(groups) if isinstance(groups, list) else set()) or dep not in remaining
                      for dep in dep_map.get(tid, []))
            ]
            
            # Simpler: tasks with no dependencies can run in parallel
            no_deps = [tid for tid in remaining if not dep_map.get(tid, set())]
            
            if no_deps:
                groups.append(no_deps)
                remaining -= set(no_deps)
            else:
                # Circular dependency or stuck - add remaining as single group
                groups.append(list(remaining))
                break
        
        return groups
    
    def _create_execution_order(self, tasks: List[SubTask], 
                                 parallel_groups: List[List[str]]) -> List[str]:
        """Create flattened execution order."""
        order = []
        for group in parallel_groups:
            order.extend(group)
        return order
    
    def _estimate_duration(self, tasks: List[SubTask]) -> float:
        """Estimate total duration in milliseconds."""
        # Base estimates per task type
        estimates = {
            "planner": 5000,
            "architect": 8000,
            "code_generator": 30000,
            "frontend_dev": 25000,
            "tester": 20000,
            "debugger": 15000,
            "reviewer": 10000,
            "devops": 12000,
            "general": 20000,
        }
        
        total = sum(estimates.get(t.assigned_agent, 20000) for t in tasks)
        
        # Parallel reduction (approximate)
        max_parallel = max(len(g) for g in self._identify_parallel_groups(tasks))
        if max_parallel > 1:
            total /= min(max_parallel, self.max_parallel)
        
        return total
    
    def execute(self, plan: OrchestrationPlan, 
                executor_func: Callable[[SubTask], Dict]) -> Dict[str, Any]:
        """
        Execute the plan with parallel sub-agents.
        
        Args:
            plan: The orchestration plan
            executor_func: Function to execute each subtask
            
        Returns:
            Execution results with timing and success/failure info
        """
        start_time = time.time()
        results = {
            "plan_id": len(self.plans),
            "total_tasks": len(plan.tasks),
            "task_results": {},
            "failed_tasks": [],
            "success": True,
        }
        
        # Execute by parallel groups
        for group in plan.parallel_groups:
            group_tasks = [t for t in plan.tasks if t.id in group]
            
            # Parallel execution within group
            with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
                futures = {
                    executor.submit(self._execute_with_retry, task, executor_func): task
                    for task in group_tasks
                }
                
                for future in as_completed(futures):
                    task = futures[future]
                    try:
                        result = future.result()
                        results["task_results"][task.id] = result
                        task.status = TaskStatus.COMPLETED
                    except Exception as e:
                        results["failed_tasks"].append(task.id)
                        results["success"] = False
                        task.status = TaskStatus.FAILED
                        task.error = str(e)
        
        results["duration_ms"] = (time.time() - start_time) * 1000
        results["estimated_vs_actual"] = {
            "estimated": plan.estimated_duration_ms,
            "actual": results["duration_ms"]
        }
        
        self.execution_history.append(results)
        return results
    
    def _execute_with_retry(self, task: SubTask, 
                            executor_func: Callable[[SubTask], Dict]) -> Dict:
        """Execute a single task with retries."""
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        
        for attempt in range(self.max_retries + 1):
            try:
                result = executor_func(task)
                task.end_time = time.time()
                task.result = result
                return result
            except Exception as e:
                if attempt < self.max_retries:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    task.end_time = time.time()
                    task.error = str(e)
                    raise
        
        raise Exception(f"Failed after {self.max_retries} retries")
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status."""
        return {
            "total_plans": len(self.plans),
            "total_executions": len(self.execution_history),
            "success_rate": self._calculate_success_rate(),
            "avg_duration_ms": self._calculate_avg_duration(),
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if not self.execution_history:
            return 0.0
        successes = sum(1 for e in self.execution_history if e["success"])
        return successes / len(self.execution_history)
    
    def _calculate_avg_duration(self) -> float:
        """Calculate average execution duration."""
        if not self.execution_history:
            return 0.0
        total = sum(e["duration_ms"] for e in self.execution_history)
        return total / len(self.execution_history)
    
    def _topological_sort(self, tasks: List[SubTask]) -> List[List[str]]:
        """
        Topological sort of tasks based on dependencies.
        
        Returns list of groups where tasks in each group can run in parallel,
        and groups are ordered by dependency.
        
        Args:
            tasks: List of tasks with dependencies
            
        Returns:
            List of task ID groups in execution order
        """
        # Build adjacency and in-degree maps
        in_degree: Dict[str, int] = {t.id: 0 for t in tasks}
        dependents: Dict[str, Set[str]] = {t.id: set() for t in tasks}
        
        for task in tasks:
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.id] += 1
                    dependents[dep].add(task.id)
        
        # Kahn's algorithm with parallel grouping
        groups: List[List[str]] = []
        remaining = set(t.id for t in tasks)
        
        while remaining:
            # Find all tasks with no remaining dependencies
            ready = [tid for tid in remaining if in_degree[tid] == 0]
            
            if not ready:
                # Circular dependency - break remaining
                ready = list(remaining)
            
            groups.append(ready)
            
            # Remove ready tasks and update in-degrees
            for tid in ready:
                remaining.remove(tid)
                for dependent in dependents.get(tid, set()):
                    if dependent in in_degree:
                        in_degree[dependent] -= 1
        
        return groups
    
    async def execute_parallel_subtasks(
        self,
        subtasks: List[Dict[str, Any]],
        executor_func: Callable[[Dict], Any],
        max_parallel: int = 4
    ) -> Dict[str, Any]:
        """
        Execute subtasks in parallel using asyncio.
        
        Groups tasks by dependencies - independent tasks run together.
        Respects rate limits across providers.
        
        Args:
            subtasks: List of subtask dictionaries with:
                - id: Unique identifier
                - description: Task description
                - dependencies: List of task IDs this depends on
                - priority: Task priority (higher = more important)
                - provider: Optional preferred provider
            executor_func: Async function to execute each subtask
            max_parallel: Maximum parallel executions
            
        Returns:
            Dict with results, timing, and success/failure info
        """
        start_time = time.time()
        results: Dict[str, Any] = {
            "task_results": {},
            "failed_tasks": [],
            "success": True,
        }
        
        # Convert to SubTask objects
        tasks = [
            SubTask(
                id=st.get("id", f"task_{i}"),
                description=st.get("description", ""),
                assigned_agent=st.get("agent", "general"),
                priority=st.get("priority", 5),
                dependencies=st.get("dependencies", []),
            )
            for i, st in enumerate(subtasks)
        ]
        
        # Get execution order using topological sort
        execution_groups = self._topological_sort(tasks)
        
        if _rate_limiter:
            _rate_limiter.wait_if_needed("gemini")
        
        # Execute each group in parallel
        semaphore = asyncio.Semaphore(max_parallel)
        
        async def execute_with_semaphore(task_id: str, task: SubTask) -> Tuple[str, Any]:
            async with semaphore:
                try:
                    # Check rate limits before execution
                    result = await executor_func({
                        "id": task.id,
                        "description": task.description,
                        "assigned_agent": task.assigned_agent,
                        "priority": task.priority,
                    })
                    
                    # Record rate limit usage
                    if _rate_limiter:
                        _rate_limiter.record_request("gemini")
                    
                    return task_id, {"success": True, "result": result}
                except Exception as e:
                    return task_id, {"success": False, "error": str(e)}
        
        # Run all groups
        for group in execution_groups:
            group_tasks = [t for t in tasks if t.id in group]
            
            # Create tasks for this group
            async_tasks = [
                execute_with_semaphore(t.id, t)
                for t in group_tasks
            ]
            
            # Execute group in parallel
            group_results = await asyncio.gather(*async_tasks)
            
            # Process results
            for task_id, result in group_results:
                results["task_results"][task_id] = result
                if not result.get("success"):
                    results["failed_tasks"].append(task_id)
                    results["success"] = False
        
        results["duration_ms"] = (time.time() - start_time) * 1000
        results["total_tasks"] = len(subtasks)
        results["parallel_groups"] = len(execution_groups)
        
        return results
    
    async def execute_distributed(
        self,
        subtasks: List[Dict[str, Any]],
        executor_func: Callable[[Dict], Any],
        provider_distribution: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Execute subtasks distributed across multiple providers.
        
        Args:
            subtasks: List of subtask dictionaries
            executor_func: Async function to execute each subtask
            provider_distribution: Dict of provider -> weight (for load balancing)
            
        Returns:
            Dict with results and provider usage statistics
        """
        provider_distribution = provider_distribution or {
            "gemini": 0.5,
            "groq": 0.3,
            "openrouter": 0.2,
        }
        
        start_time = time.time()
        results: Dict[str, Any] = {
            "task_results": {},
            "failed_tasks": [],
            "provider_usage": defaultdict(int),
            "success": True,
        }
        
        # Assign providers based on distribution
        import random
        providers = list(provider_distribution.keys())
        weights = list(provider_distribution.values())
        
        for subtask in subtasks:
            # Assign provider based on weighted random
            provider = random.choices(providers, weights=weights)[0]
            subtask["provider"] = provider
            results["provider_usage"][provider] += 1
        
        # Execute with rate limiting per provider
        semaphores = {
            provider: asyncio.Semaphore(max(1, int(4 * weight)))
            for provider, weight in provider_distribution.items()
        }
        
        async def execute_with_provider(task_id: str, task: Dict) -> Tuple[str, Any]:
            provider = task.get("provider", "gemini")
            async with semaphores.get(provider, asyncio.Semaphore(1)):
                try:
                    # Wait for rate limit
                    if _rate_limiter:
                        _rate_limiter.wait_if_needed(provider)
                    
                    # Execute
                    result = await executor_func(task)
                    _rate_limiter.record_request(provider)
                    
                    return task_id, {"success": True, "result": result, "provider": provider}
                except Exception as e:
                    return task_id, {"success": False, "error": str(e), "provider": provider}
        
        # Execute all tasks
        tasks = [
            execute_with_provider(st.get("id", f"task_{i}"), st)
            for i, st in enumerate(subtasks)
        ]
        
        all_results = await asyncio.gather(*tasks)
        
        # Process results
        for task_id, result in all_results:
            results["task_results"][task_id] = result
            if not result.get("success"):
                results["failed_tasks"].append(task_id)
                results["success"] = False
        
        results["duration_ms"] = (time.time() - start_time) * 1000
        results["total_tasks"] = len(subtasks)
        results["provider_usage"] = dict(results["provider_usage"])
        
        return results


def quick_orchestrate(task: str, context: Dict = None) -> Dict[str, Any]:
    """
    Quick orchestration of a task.
    
    Usage:
        from neuro.skills.multi_agent import quick_orchestrate
        
        results = quick_orchestrate("Build a REST API with tests", {
            "working_dir": "/path/to/project"
        })
    """
    orchestrator = MultiAgentOrchestrator()
    
    # Create plan
    plan = orchestrator.create_plan(task, context)
    
    # Execute with Neuro's agent loop
    def neuro_executor(subtask):
        # Use Neuro's existing agent loop
        from neuro.executor.agent_loop import run_goal
        result = run_goal(
            goal=subtask.description,
            working_dir=context.get("working_dir", ".") if context else ".",
            use_skills=True,
            verbose=False
        )
        return vars(result) if result else {}
    
    results = orchestrator.execute(plan, neuro_executor)
    
    return {
        "plan": {
            "tasks": [{"id": t.id, "description": t.description, "assigned_agent": t.assigned_agent} 
                      for t in plan.tasks],
            "parallel_groups": plan.parallel_groups,
            "estimated_duration_ms": plan.estimated_duration_ms
        },
        "results": results
    }


# SKILL.md content
SKILL_MD = """
---
name: multi-agent-orchestration
description: Multi-agent task decomposition and parallel execution
triggers:
  - multi
  - orchestrate
  - parallel
  - distribute
  - swarm
  - decompose
---

# Multi-Agent Orchestration Skill

Advanced multi-agent orchestration inspired by ECC's /multi-plan, /multi-execute patterns.
Enhanced from your basic agent swarm.

## Features

### 1. Smart Task Decomposition
Automatically breaks down complex tasks into subtasks:
- Identifies dependencies
- Groups parallelizable tasks
- Assigns appropriate agents

### 2. Parallel Execution
Executes tasks in parallel with:
- Configurable max parallelism (default: 4)
- Retry logic with exponential backoff
- Thread-safe execution

### 3. Intelligent Planning
Creates execution plans that:
- Respect task dependencies
- Optimize for parallelism
- Estimate duration

## Usage

```python
from neuro.skills.multi_agent import MultiAgentOrchestrator, quick_orchestrate

# Quick orchestration (automatic planning + execution)
results = quick_orchestrate("Build a web app with tests", {
    "working_dir": "/path/to/project"
})

# Custom orchestration
orchestrator = MultiAgentOrchestrator(max_parallel=4, max_retries=2)
plan = orchestrator.create_plan("Build a REST API", context)

# Execute with custom executor
results = orchestrator.execute(plan, my_executor_func)

# Check status
status = orchestrator.get_status()
```

## Task Types

| Task | Agent | Priority |
|------|-------|----------|
| planning | planner | 10 |
| architecture | architect | 9 |
| backend | code_generator | 7 |
| frontend | frontend_dev | 7 |
| testing | tester | 6 |
| debugging | debugger | 10 |
| review | reviewer | 8 |
| deployment | devops | 5 |

## Integration with Neuro

Use with your existing router:
```python
# Tasks are automatically routed based on assigned_agent
# Backend → DeepSeek V4 Flash (coding optimized)
# Testing → Qwen3 Coder (test generation)
# Review → Llama 3.3 70B (70B model for review)
```
"""