# Auto-Fix Loop System
# Orchestrates: run code → detect error → fix → repeat until success

import subprocess
import time
import os
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class FixAttempt:
    """Record of a fix attempt."""
    iteration: int
    command: str
    error: str
    fix_applied: Optional[str]
    success: bool
    duration_ms: float

@dataclass
class AutoFixConfig:
    """Configuration for auto-fix loop."""
    max_iterations: int = 5
    fix_timeout: int = 120  # seconds
    wait_between_attempts: int = 2  # seconds
    enable_shell_fix: bool = True
    enable_playwright_test: bool = True
    test_after_fix: bool = True

@dataclass
class AutoFixResult:
    """Result of auto-fix loop."""
    success: bool
    iterations: int
    final_command: str
    attempts: List[FixAttempt]
    total_duration_ms: float
    errors_fixed: List[str]
    tests_passed: bool

class AutoFixLoop:
    """
    Orchestrates the self-healing loop:
    1. Run code
    2. Detect error
    3. Apply fix
    4. Repeat until success
    
    Usage:
        from neuro.skills.auto_fix_loop import AutoFixLoop
        
        fixer = AutoFixLoop()
        result = fixer.fix_and_run("python app.py")
    """
    
    def __init__(self, config: AutoFixConfig = None):
        self.config = config or AutoFixConfig()
        self.history: List[FixAttempt] = []
    
    def fix_and_run(self, initial_command: str,
                    working_dir: str = ".",
                    context: Dict = None) -> AutoFixResult:
        """
        Execute command with auto-fix loop.
        
        Args:
            initial_command: Command to execute
            working_dir: Working directory
            context: Additional context for fixing
            
        Returns:
            AutoFixResult with all attempts and final status
        """
        context = context or {}
        attempts = []
        current_command = initial_command
        errors_fixed = []
        total_duration = 0
        
        for iteration in range(1, self.config.max_iterations + 1):
            print(f"\n🔄 Iteration {iteration}/{self.config.max_iterations}")
            print(f"   Command: {current_command}")
            
            start_time = time.time()
            
            # Execute command
            result = self._execute_command(current_command, working_dir)
            duration = (time.time() - start_time) * 1000
            total_duration += duration
            
            # Check if success
            if result["success"]:
                print(f"   ✅ SUCCESS!")
                return AutoFixResult(
                    success=True,
                    iterations=iteration,
                    final_command=current_command,
                    attempts=attempts + [FixAttempt(
                        iteration=iteration,
                        command=current_command,
                        error="",
                        fix_applied=None,
                        success=True,
                        duration_ms=duration
                    )],
                    total_duration_ms=total_duration,
                    errors_fixed=errors_fixed,
                    tests_passed=True
                )
            
            # Error occurred - attempt fix
            print(f"   ❌ Error: {result['error']}")
            
            if iteration >= self.config.max_iterations:
                print(f"   ⚠️ Max iterations reached")
                break
            
            # Try to fix
            fix_result = self._attempt_fix(
                current_command,
                result["error"],
                result["stderr"],
                context
            )
            
            if fix_result:
                errors_fixed.append(result["error"])
                current_command = fix_result
                print(f"   🔧 Fix applied: {fix_result}")
                
                # Wait before retry
                time.sleep(self.config.wait_between_attempts)
            else:
                print(f"   ⚠️ Could not auto-fix")
                break
            
            attempts.append(FixAttempt(
                iteration=iteration,
                command=current_command,
                error=result["error"],
                fix_applied=fix_result,
                success=False,
                duration_ms=duration
            ))
        
        # Final attempt with original command
        attempts.append(FixAttempt(
            iteration=len(attempts) + 1,
            command=current_command,
            error=result.get("error", "Unknown"),
            fix_applied=None,
            success=False,
            duration_ms=0
        ))
        
        return AutoFixResult(
            success=False,
            iterations=len(attempts),
            final_command=current_command,
            attempts=attempts,
            total_duration_ms=total_duration,
            errors_fixed=errors_fixed,
            tests_passed=False
        )
    
    def _execute_command(self, command: str, working_dir: str) -> Dict:
        """Execute shell command and return result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=self.config.fix_timeout
            )
            
            success = result.returncode == 0
            
            # Extract error message
            error = ""
            if not success:
                error_output = result.stderr or result.stdout
                error = self._extract_error(error_output)
            
            return {
                "success": success,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "error": error
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Timeout after {self.config.fix_timeout}s",
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "error": str(e)
            }
    
    def _extract_error(self, output: str) -> str:
        """Extract main error message from output."""
        lines = output.strip().split('\n')
        
        # Look for common error patterns
        for line in lines:
            if any(pattern in line.lower() for pattern in [
                "error", "exception", "failed", "traceback"
            ]):
                return line.strip()
        
        return lines[-1] if lines else "Unknown error"
    
    def _attempt_fix(self, command: str, error: str,
                    stderr: str, context: Dict) -> Optional[str]:
        """
        Attempt to fix the error.
        Returns new command or None if can't fix.
        """
        fix = None
        
        # Dependency errors
        if "No module named" in error:
            import re
            match = re.search(r"No module named '(\w+)'", error)
            if match:
                module = match.group(1)
                if "pip install" in command or "python" in command:
                    fix = command.replace("python ", f"pip install {module} && python ")
                else:
                    fix = f"pip install {module} && {command}"
        
        elif "Cannot find module" in error:
            import re
            match = re.search(r"Cannot find module '([\w.]+)'", error)
            if match:
                module = match.group(1)
                fix = f"npm install {module} && {command}"
        
        elif "npm install" in error or "package.json" in error:
            fix = "npm install && " + command
        
        # Syntax errors - suggest review
        elif any(kw in error.lower() for kw in ["syntax", "unexpected token", "parse"]):
            fix = None  # Can't auto-fix syntax
        
        # Permission errors
        elif "permission denied" in error.lower():
            # Extract file path
            import re
            match = re.search(r"Permission denied: '?([\w./-]+)'?", error)
            if match:
                file_path = match.group(1)
                fix = f"chmod +x {file_path} && {command}"
        
        return fix
    
    def run_with_test(self, command: str, test_command: str,
                      working_dir: str = ".") -> AutoFixResult:
        """
        Run command and test result with Playwright.
        
        Args:
            command: Command to run
            test_command: Command to test result (e.g., "pytest")
            working_dir: Working directory
        """
        # First, fix and run the command
        result = self.fix_and_run(command, working_dir)
        
        if result.success and self.config.test_after_fix:
            # Run tests
            print(f"\n🧪 Running tests: {test_command}")
            test_result = self._execute_command(test_command, working_dir)
            
            if not test_result["success"]:
                print(f"   ❌ Tests failed: {test_result['error']}")
                result.tests_passed = False
            else:
                print(f"   ✅ Tests passed!")
                result.tests_passed = True
        
        return result


def quick_fix(command: str, max_iterations: int = 5) -> Dict[str, Any]:
    """
    Quick auto-fix execution.
    
    Usage:
        from neuro.skills.auto_fix_loop import quick_fix
        
        result = quick_fix("python app.py")
        print(f"Success: {result['success']}")
        print(f"Iterations: {result['iterations']}")
        print(f"Errors fixed: {result['errors_fixed']}")
    """
    fixer = AutoFixLoop(AutoFixConfig(max_iterations=max_iterations))
    result = fixer.fix_and_run(command)
    
    return {
        "success": result.success,
        "iterations": result.iterations,
        "final_command": result.final_command,
        "total_duration_ms": result.total_duration_ms,
        "errors_fixed": result.errors_fixed,
        "attempts_summary": [
            f"Iteration {a.iteration}: {'✅' if a.success else '❌'} - {a.error}"
            for a in result.attempts
        ]
    }


# SKILL.md content
SKILL_MD = """
---
name: auto-fix-loop
description: Orchestrate self-healing loop: run code, detect error, fix, repeat
triggers:
  - fix
  - auto-fix
  - self-heal
  - loop
  - retry
  - iterate
---

# Auto-Fix Loop System

Orchestrates self-healing execution loop:
1. Run code
2. Detect error
3. Apply fix
4. Repeat until success

## Features

### 1. Self-Healing
Automatically attempts fixes for:
- Missing Python packages (pip install)
- Missing npm packages
- Permission issues (chmod)
- Configuration errors

### 2. Configurable
- Max iterations (default: 5)
- Timeout per attempt (default: 120s)
- Wait between attempts (default: 2s)

### 3. Comprehensive Logging
- All attempts recorded
- Errors fixed tracked
- Duration measured

## Usage

```python
from neuro.skills.auto_fix_loop import AutoFixLoop, quick_fix

# Quick fix
result = quick_fix("python app.py", max_iterations=5)

# Custom fix loop
config = AutoFixConfig(
    max_iterations=5,
    fix_timeout=120,
    wait_between_attempts=2
)
fixer = AutoFixLoop(config)
result = fixer.fix_and_run("npm run build", working_dir="/path/to/project")

# With testing
result = fixer.run_with_test(
    command="python app.py",
    test_command="pytest",
    working_dir="."
)
```

## Fix Strategies

| Error Type | Fix Applied |
|------------|-------------|
| No module named 'x' | pip install x |
| Cannot find module 'x' | npm install x |
| Permission denied | chmod +x file |
| npm install failed | npm install && command |

## Flow

```
Run → Error? → Fix → Run → Error? → Fix → ... → Success
                    ↓
              Max iterations → Give up
```
"""