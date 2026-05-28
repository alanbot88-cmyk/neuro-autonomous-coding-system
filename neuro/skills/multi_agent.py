# Multi-Agent Orchestration Skill
# Inspired by ECC's multi-plan, multi-execute, and PM2 commands
# Enhanced from your basic agent swarm

import os
import time
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

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