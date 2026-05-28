# Autonomous Loop Skill
# Inspired by ECC's autonomous-loops patterns
# Self-improvement through iterative execution and learning

import time
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

class LoopType(Enum):
    SEQUENTIAL = "sequential"  # One task after another
    PARALLEL = "parallel"  # Multiple tasks simultaneously
    PR_LOOP = "pr_loop"  # PR review and fix cycle
    DAG = "dag"  # Directed Acyclic Graph execution

@dataclass
class LoopConfig:
    """Configuration for autonomous loop."""
    max_iterations: int = 3
    convergence_threshold: float = 0.85  # Stop if 85% similar to previous
    timeout_seconds: int = 300
    checkpoint_interval: int = 60  # Save state every 60 seconds
    early_exit_conditions: List[str] = field(default_factory=list)

@dataclass
class LoopIteration:
    """Single iteration of the loop."""
    iteration: int
    input_data: Any
    output_data: Any
    convergence_score: float  # How much changed from previous
    duration_ms: float
    status: str  # "running", "converged", "max_iterations", "timeout", "error"

class AutonomousLoop:
    """
    Self-improving autonomous loop system.
    Inspired by ECC's autonomous-loops patterns.
    
    Usage:
        from neuro.skills.autonomous_loop import AutonomousLoop, run_autonomous_loop
        
        loop = AutonomousLoop(loop_type=LoopType.SEQUENTIAL)
        results = loop.run(
            task="Fix all bugs in auth module",
            executor_func=my_executor
        )
    """
    
    def __init__(self, loop_type: LoopType = LoopType.SEQUENTIAL, config: LoopConfig = None):
        self.loop_type = loop_type
        self.config = config or LoopConfig()
        self.history: List[LoopIteration] = []
        self.checkpoints: List[Dict] = []
    
    def run(self, task: str, executor_func: Callable, 
            context: Dict = None) -> Dict[str, Any]:
        """
        Run the autonomous loop.
        
        Args:
            task: The task to execute
            executor_func: Function that executes one iteration
            context: Additional context
            
        Returns:
            Loop results with convergence info
        """
        context = context or {}
        start_time = time.time()
        
        results = {
            "task": task,
            "iterations": [],
            "final_output": None,
            "status": "running",
            "total_duration_ms": 0,
            "converged": False
        }
        
        prev_output = None
        iteration_count = 0
        
        while iteration_count < self.config.max_iterations:
            iteration_count += 1
            
            # Check timeout
            if (time.time() - start_time) > self.config.timeout_seconds:
                results["status"] = "timeout"
                break
            
            # Execute iteration
            iter_start = time.time()
            
            try:
                output = executor_func(task, prev_output, iteration_count, context)
            except Exception as e:
                results["status"] = "error"
                results["error"] = str(e)
                break
            
            iter_duration = (time.time() - iter_start) * 1000
            
            # Calculate convergence
            convergence = self._calculate_convergence(prev_output, output)
            
            iteration = LoopIteration(
                iteration=iteration_count,
                input_data=task,
                output_data=output,
                convergence_score=convergence,
                duration_ms=iter_duration,
                status="running"
            )
            
            self.history.append(iteration)
            results["iterations"].append({
                "iteration": iteration_count,
                "convergence": convergence,
                "duration_ms": iter_duration,
                "output_summary": self._summarize_output(output)
            })
            
            # Check early exit conditions
            if convergence >= self.config.convergence_threshold:
                iteration.status = "converged"
                results["status"] = "converged"
                results["converged"] = True
                results["final_output"] = output
                break
            
            # Check custom early exit
            for condition in self.config.early_exit_conditions:
                if self._check_condition(condition, output):
                    results["status"] = "early_exit"
                    results["final_output"] = output
                    break
            
            # Save checkpoint
            if iteration_count % self.config.checkpoint_interval == 0:
                self._save_checkpoint(iteration_count, output)
            
            prev_output = output
        
        if iteration_count >= self.config.max_iterations:
            results["status"] = "max_iterations"
            results["final_output"] = prev_output
        
        results["total_duration_ms"] = (time.time() - start_time) * 1000
        results["iterations_run"] = iteration_count
        
        return results
    
    def _calculate_convergence(self, prev: Any, current: Any) -> float:
        """
        Calculate how much the output changed from previous iteration.
        Returns 1.0 if no change (fully converged), 0.0 if completely different.
        """
        if prev is None:
            return 0.0  # First iteration, no comparison
        
        try:
            # For dictionaries (code output)
            if isinstance(prev, dict) and isinstance(current, dict):
                prev_str = json.dumps(prev, sort_keys=True)
                curr_str = json.dumps(current, sort_keys=True)
                
                # Simple similarity based on length and content
                if prev_str == curr_str:
                    return 1.0
                
                # Count common elements
                common = sum(1 for k in prev if k in current and prev[k] == current[k])
                total = max(len(prev), len(current), 1)
                return common / total
            
            # For strings (code/text)
            if isinstance(prev, str) and isinstance(current, str):
                if prev == current:
                    return 1.0
                
                # Character-level similarity
                common = sum(1 for c in prev if c in current)
                total = max(len(prev), len(current), 1)
                return common / total
            
            # Default: partial convergence
            return 0.5
        
        except Exception:
            return 0.5
    
    def _summarize_output(self, output: Any) -> str:
        """Create a brief summary of the output."""
        if output is None:
            return "None"
        
        if isinstance(output, dict):
            keys = list(output.keys())[:3]
            return f"Dict with keys: {keys}"
        
        if isinstance(output, str):
            return output[:100] + "..." if len(output) > 100 else output
        
        return str(type(output))
    
    def _check_condition(self, condition: str, output: Any) -> bool:
        """Check if early exit condition is met."""
        if condition == "tests_pass":
            if isinstance(output, dict) and output.get("tests_passed"):
                return True
        
        if condition == "no_errors":
            if isinstance(output, dict) and not output.get("errors"):
                return True
        
        return False
    
    def _save_checkpoint(self, iteration: int, output: Any):
        """Save checkpoint for recovery."""
        checkpoint = {
            "iteration": iteration,
            "timestamp": time.time(),
            "output": output
        }
        self.checkpoints.append(checkpoint)
    
    def get_history(self) -> List[Dict]:
        """Get loop execution history."""
        return [
            {
                "iteration": h.iteration,
                "convergence": h.convergence_score,
                "duration_ms": h.duration_ms,
                "status": h.status
            }
            for h in self.history
        ]
    
    def get_best_iteration(self) -> Optional[LoopIteration]:
        """Get the iteration with highest convergence (most refined)."""
        if not self.history:
            return None
        
        return max(self.history, key=lambda h: h.convergence_score)


def run_autonomous_loop(task: str, executor_func: Callable,
                        loop_type: str = "sequential",
                        max_iterations: int = 3) -> Dict[str, Any]:
    """
    Quick autonomous loop execution.
    
    Usage:
        from neuro.skills.autonomous_loop import run_autonomous_loop
        
        results = run_autonomous_loop(
            task="Fix bugs in auth.py",
            executor_func=lambda task, prev, iter_num, ctx: fix_bugs(task),
            loop_type="sequential",
            max_iterations=3
        )
    """
    loop_type_enum = LoopType.SEQUENTIAL
    if loop_type == "parallel":
        loop_type_enum = LoopType.PARALLEL
    elif loop_type == "pr_loop":
        loop_type_enum = LoopType.PR_LOOP
    elif loop_type == "dag":
        loop_type_enum = LoopType.DAG
    
    config = LoopConfig(max_iterations=max_iterations)
    loop = AutonomousLoop(loop_type=loop_type_enum, config=config)
    
    return loop.run(task, executor_func)


# PR Loop specialized implementation
class PRLoop:
    """
    Specialized loop for PR review and fix cycles.
    Inspired by ECC's PR loop patterns.
    """
    
    def __init__(self, max_cycles: int = 3):
        self.max_cycles = max_cycles
    
    def run(self, pr_url: str, reviewer_func: Callable, 
            fixer_func: Callable) -> Dict[str, Any]:
        """
        Run PR review-fix cycles.
        
        Args:
            pr_url: PR URL to review
            reviewer_func: Function to review PR and find issues
            fixer_func: Function to fix found issues
        """
        results = {
            "pr_url": pr_url,
            "cycles": [],
            "final_status": "in_progress"
        }
        
        for cycle in range(self.max_cycles):
            # Review PR
            review_results = reviewer_func(pr_url, cycle + 1)
            
            # Check if issues found
            if not review_results.get("issues", []):
                results["final_status"] = "approved"
                results["cycles"].append({
                    "cycle": cycle + 1,
                    "issues_found": 0,
                    "status": "approved"
                })
                break
            
            # Fix issues
            fixes = fixer_func(review_results["issues"])
            
            results["cycles"].append({
                "cycle": cycle + 1,
                "issues_found": len(review_results.get("issues", [])),
                "fixes_applied": len(fixes.get("applied", [])),
                "status": "fixed"
            })
        
        return results


# SKILL.md content
SKILL_MD = """
---
name: autonomous-loops
description: Self-improving autonomous loop with convergence detection
triggers:
  - loop
  - iterate
  - converge
  - improve
  - autonomous
  - self-improve
---

# Autonomous Loop Skill

Self-improving autonomous execution inspired by ECC's autonomous-loops patterns.

## Features

### 1. Convergence Detection
Automatically detects when output stops changing:
- Stops after reaching threshold (default: 85%)
- Avoids unnecessary iterations
- Saves computation time

### 2. Multiple Loop Types
- **sequential**: One task after another
- **parallel**: Multiple tasks simultaneously  
- **pr_loop**: PR review and fix cycles
- **dag**: Directed Acyclic Graph execution

### 3. Checkpointing
Saves state periodically for:
- Recovery from failures
- Resume interrupted loops
- Debugging

### 4. Early Exit Conditions
Configurable early exit:
- "tests_pass" - Exit if tests pass
- "no_errors" - Exit if no errors
- Custom conditions

## Usage

```python
from neuro.skills.autonomous_loop import AutonomousLoop, run_autonomous_loop

# Simple loop
loop = AutonomousLoop(loop_type=LoopType.SEQUENTIAL)
results = loop.run(
    task="Fix bugs in auth.py",
    executor_func=lambda task, prev, iter_num, ctx: fix_bugs(task)
)

# Quick loop
results = run_autonomous_loop(
    task="Refactor code",
    executor_func=my_executor,
    max_iterations=3
)

# Check results
print(f"Status: {results['status']}")
print(f"Iterations: {results['iterations_run']}")
print(f"Converged: {results['converged']}")
```

## PR Loop

```python
from neuro.skills.autonomous_loop import PRLoop

pr_loop = PRLoop(max_cycles=3)
results = pr_loop.run(
    pr_url="https://github.com/owner/repo/pull/123",
    reviewer_func=review_pr,
    fixer_func=fix_issues
)
```

## Convergence Calculation

Convergence = 1.0 when output stops changing:
- Dict comparison: Match keys/values
- String comparison: Character overlap
- 0.0 = completely different
- 1.0 = identical (converged)

## Integration with Neuro

Use with your multi-agent orchestrator:
```python
# Auto-improve code generation
loop = AutonomousLoop()
results = loop.run(
    task="Generate REST API",
    executor_func=lambda t, p, i, c: generate_api(t)
)

# Use best iteration output
best = loop.get_best_iteration()
final_code = best.output_data
```
"""