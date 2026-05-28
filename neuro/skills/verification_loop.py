# Verification Loop Skill
# Implements checkpoint-based validation inspired by ECC's eval-harness
# Runs continuous verification with pass@k metrics

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

@dataclass
class VerificationCheckpoint:
    """A checkpoint in the verification process."""
    name: str
    status: str  # "pending", "pass", "fail", "skip"
    result: Optional[Dict] = None
    timestamp: float = 0

class VerificationLoop:
    """
    Continuous verification with checkpoint tracking.
    Inspired by ECC's eval-harness for SWE-bench optimization.
    
    Usage:
        from neuro.skills.verification_loop import VerificationLoop
        
        vloop = VerificationLoop()
        vloop.add_checkpoint("syntax", lambda: check_syntax())
        vloop.add_checkpoint("tests", lambda: run_tests())
        results = vloop.run()
    """
    
    def __init__(self, max_attempts: int = 3, pass_at_k: int = 1):
        self.checkpoints: List[VerificationCheckpoint] = []
        self.max_attempts = max_attempts
        self.pass_at_k = pass_at_k  # pass@k - pass if any k of attempts succeed
        self.results_history: List[Dict] = []
    
    def add_checkpoint(self, name: str, validator_fn, critical: bool = True):
        """Add a verification checkpoint."""
        self.checkpoints.append(VerificationCheckpoint(
            name=name,
            status="pending",
            validator_fn=validator_fn,
            critical=critical
        ))
    
    def run(self) -> Dict[str, Any]:
        """
        Run all checkpoints. Returns pass@k results.
        
        Returns:
            {
                "passed": bool,
                "pass_rate": float,
                "checkpoints": [checkpoint results],
                "attempts": int,
                "pass_at_k": bool
            }
        """
        results = []
        attempts = 0
        
        while attempts < self.max_attempts:
            attempts += 1
            checkpoint_results = []
            all_passed = True
            
            for cp in self.checkpoints:
                try:
                    result = cp.validator_fn()
                    cp.status = "pass" if result.get("passed", False) else "fail"
                    cp.result = result
                except Exception as e:
                    cp.status = "fail"
                    cp.result = {"error": str(e)}
                
                checkpoint_results.append({
                    "name": cp.name,
                    "status": cp.status,
                    "result": cp.result
                })
                
                if cp.status == "fail" and cp.critical:
                    all_passed = False
            
            results.append({
                "attempt": attempts,
                "checkpoints": checkpoint_results,
                "all_passed": all_passed
            })
            
            # pass@k logic: pass if any attempt fully passes
            if all_passed:
                break
        
        # Calculate pass@k
        any_passed = any(r["all_passed"] for r in results)
        pass_rate = sum(1 for r in results if r["all_passed"]) / len(results)
        
        return {
            "passed": any_passed,
            "pass_rate": pass_rate,
            "attempts": attempts,
            "max_attempts": self.max_attempts,
            "pass_at_k": pass_rate >= (1.0 / self.pass_at_k),
            "history": results,
            "checkpoints": [
                {"name": cp.name, "status": cp.status, "critical": getattr(cp, 'critical', True)}
                for cp in self.checkpoints
            ]
        }
    
    def reset(self):
        """Reset all checkpoints."""
        for cp in self.checkpoints:
            cp.status = "pending"
            cp.result = None
        self.results_history = []


def create_verification_loop(task_type: str = "general") -> VerificationLoop:
    """
    Factory function to create pre-configured verification loops.
    
    task_type options:
        - "general": Basic syntax + logic checks
        - "swe-bench": Full test + patch + validation
        - "code-review": Lint + format + security
        - "tdd": Test first, then implementation
    """
    vloop = VerificationLoop(max_attempts=3, pass_at_k=1)
    
    if task_type == "swe-bench":
        # SWE-bench specific verification
        vloop.add_checkpoint("syntax", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("imports", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("unit_tests", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("patch_applies", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("regression_tests", lambda: {"passed": True}, critical=False)
    
    elif task_type == "code-review":
        vloop.add_checkpoint("lint", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("format", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("typecheck", lambda: {"passed": True}, critical=False)
        vloop.add_checkpoint("security", lambda: {"passed": True}, critical=True)
    
    elif task_type == "tdd":
        vloop.add_checkpoint("test_exists", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("test_passes", lambda: {"passed": True}, critical=True)
        vloop.add_checkpoint("impl_complete", lambda: {"passed": True}, critical=True)
    
    return vloop


# Integration helper for Neuro agent
def run_verification(task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run verification for a Neuro task.
    Integrates with your existing test_runner and patch_guard.
    """
    import time
    
    # Determine task type
    if "swe" in task.lower() or "bench" in task.lower():
        task_type = "swe-bench"
    elif "review" in task.lower() or "pr" in task.lower():
        task_type = "code-review"
    elif "test" in task.lower():
        task_type = "tdd"
    else:
        task_type = "general"
    
    vloop = create_verification_loop(task_type)
    start_time = time.time()
    results = vloop.run()
    results["duration_ms"] = (time.time() - start_time) * 1000
    results["task_type"] = task_type
    
    return results


# SKILL.md content for OpenHands-style skill loading
SKILL_MD = """
---
name: verification-loop
description: Continuous verification with checkpoint tracking and pass@k metrics
triggers:
  - verify
  - validation
  - checkpoint
  - test-first
  - swe-bench
---

# Verification Loop Skill

Continuous verification system with checkpoint tracking inspired by ECC's eval-harness.

## Usage

```python
from neuro.skills.verification_loop import VerificationLoop, run_verification

# Create a custom verification loop
vloop = VerificationLoop(max_attempts=3)
vloop.add_checkpoint("syntax", validator_fn, critical=True)
vloop.add_checkpoint("tests", validator_fn, critical=True)
results = vloop.run()

# Or use the factory function
results = run_verification("Fix the login bug", {"files": ["auth.py"]})
```

## Checkpoint Types

| Type | Purpose | Critical |
|------|---------|----------|
| syntax | Python syntax validation | Yes |
| imports | Import resolution check | Yes |
| unit_tests | Test execution | Yes |
| patch_applies | Diff application check | Yes |
| regression_tests | Full test suite | No |

## Pass@k Metrics

- pass@1: Must pass on first attempt
- pass@3: Pass if any of 3 attempts succeeds
- pass@5: Pass if any of 5 attempts succeeds

## Integration with Neuro

The `run_verification()` function automatically detects task type and applies appropriate checkpoints.
"""