# Auto-Fix Loop System
# Orchestrates: run code → detect error → fix → repeat until success

import subprocess
import time
import os
import re
from typing import Dict, Any, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# =============================================================================
# ERROR TAXONOMY
# =============================================================================

class ErrorType(Enum):
    """Classification of error types for targeted fixing."""
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    TYPE_ERROR = "type_error"
    ASSERTION_ERROR = "assertion_error"
    TIMEOUT = "timeout"
    PERMISSION_ERROR = "permission_error"
    API_ERROR = "api_error"
    RUNTIME_ERROR = "runtime_error"
    CONNECTION_ERROR = "connection_error"
    CONFIG_ERROR = "config_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class ErrorDiagnosis:
    """
    Diagnosis of an error with classification and details.
    
    Attributes:
        error_type: Classification of the error
        message: Human-readable error message
        location: File/line where error occurred (if known)
        context: Additional context about the error
        severity: How severe the error is (1-10)
        patterns: Regex patterns found in error output
    """
    error_type: ErrorType
    message: str
    location: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    severity: int = 5
    patterns: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        loc_str = f" at {self.location}" if self.location else ""
        return f"[{self.error_type.value}] {self.message}{loc_str}"


@dataclass
class FixStrategy:
    """
    Strategy for fixing an diagnosed error.
    
    Attributes:
        strategy_type: Type of fix strategy
        description: Human-readable description
        commands: Commands to run to apply the fix
        confidence: How confident we are this will work (0-1)
        prerequisites: What needs to be in place before applying
        side_effects: Potential side effects to watch for
    """
    strategy_type: str
    description: str
    commands: List[str] = field(default_factory=list)
    confidence: float = 0.5
    prerequisites: List[str] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.strategy_type}: {self.description}"


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


# =============================================================================
# UPGRADED AUTO-FIX LOOP WITH ENHANCED SELF-HEALING
# =============================================================================

class UpgradedAutoFixLoop:
    """
    Enhanced self-healing loop with intelligent error diagnosis and targeted fixes.
    
    Features:
    - Comprehensive error taxonomy and diagnosis
    - Targeted fix strategies based on error type
    - Verification after each fix
    - Escalation when fixes fail
    
    Usage:
        from neuro.skills.auto_fix_loop import UpgradedAutoFixLoop
        
        fixer = UpgradedAutoFixLoop()
        diagnosis = fixer.diagnose(error_output)
        fix = fixer.get_targeted_fix(diagnosis)
        success = fixer.apply_and_verify(fix, test_fn)
        
        if not success:
            escalation = fixer.escalate(all_attempts)
            print(f"Manual intervention needed: {escalation}")
    """
    
    def __init__(self, max_retries: int = 5, enable_learning: bool = True):
        self.max_retries = max_retries
        self.enable_learning = enable_learning
        self.fix_history: List[Tuple[ErrorDiagnosis, FixStrategy, bool]] = []
        self.error_patterns: Dict[ErrorType, List[FixStrategy]] = {}
    
    def diagnose(self, error_output: str) -> ErrorDiagnosis:
        """
        Diagnose an error and classify it according to the error taxonomy.
        
        Args:
            error_output: The raw error output from command execution
            
        Returns:
            ErrorDiagnosis with classified error type and details
        """
        error_lower = error_output.lower()
        
        # Match against error patterns
        error_type = ErrorType.UNKNOWN_ERROR
        location = None
        context: Dict[str, Any] = {}
        patterns: List[str] = []
        severity = 5
        
        # SYNTAX_ERROR patterns
        syntax_patterns = [
            (r"syntaxerror:?\s*(.+)", 8),
            (r"syntax error", 7),
            (r"unexpected token", 7),
            (r"invalid syntax", 8),
            (r"eol while scanning", 8),
            (r"expected '[:;]", 6),
        ]
        for pattern, sev in syntax_patterns:
            match = re.search(pattern, error_lower)
            if match:
                error_type = ErrorType.SYNTAX_ERROR
                severity = sev
                patterns.append(pattern)
                break
        
        # IMPORT_ERROR patterns
        if error_type == ErrorType.UNKNOWN_ERROR:
            import_patterns = [
                (r"no module named ['\"]([\w.]+)['\"]", 7),
                (r"modulenotfounderror:? (.+)", 7),
                (r"cannot find module ['\"]([\w.]+)['\"]", 6),
                (r"import error", 6),
                (r"importerror:? (.+)", 6),
            ]
            for pattern, sev in import_patterns:
                match = re.search(pattern, error_lower)
                if match:
                    error_type = ErrorType.IMPORT_ERROR
                    severity = sev
                    patterns.append(pattern)
                    if match.groups():
                        context["missing_module"] = match.group(1)
                    break
        
        # TYPE_ERROR patterns
        if error_type == ErrorType.UNKNOWN_ERROR:
            type_patterns = [
                (r"typeerror:? (.+)", 6),
                (r"cannot (?:concatenate|add).*str.*int", 7),
                (r"'(\w+)' (?:object|instance) has no attribute", 5),
            ]
            for pattern, sev in type_patterns:
                match = re.search(pattern, error_lower)
                if match:
                    error_type = ErrorType.TYPE_ERROR
                    severity = sev
                    patterns.append(pattern)
                    break
        
        # ASSERTION_ERROR patterns
        if error_type == ErrorType.UNKNOWN_ERROR:
            if "assertionerror" in error_lower or "assert" in error_lower:
                error_type = ErrorType.ASSERTION_ERROR
                severity = 6
                patterns.append(r"assertionerror")
        
        # TIMEOUT patterns
        if error_type == ErrorType.UNKNOWN_ERROR:
            timeout_patterns = [
                (r"timeout:? (.+)", 5),
                (r"timed out", 5),
                (r"exceeded.*time", 5),
                (r"took too long", 4),
            ]
            for pattern, sev in timeout_patterns:
                if re.search(pattern, error_lower):
                    error_type = ErrorType.TIMEOUT
                    severity = sev
                    patterns.append(pattern)
                    break
        
        # PERMISSION_ERROR patterns
        if error_type == ErrorType.UNKNOWN_ERROR:
            perm_patterns = [
                (r"permission denied", 7),
                (r"permissionerror:? (.+)", 7),
                (r"eacces", 7),
                (r"not permitted", 6),
            ]
            for pattern, sev in perm_patterns:
                if re.search(pattern, error_lower):
                    error_type = ErrorType.PERMISSION_ERROR
                    severity = sev
                    patterns.append(pattern)
                    break
        
        # API_ERROR patterns
        if error_type == ErrorType.UNKNOWN_ERROR:
            api_patterns = [
                (r"api[_-]?error", 6),
                (r"rate limit", 7),
                (r"401 unauthorized", 8),
                (r"403 forbidden", 8),
                (r"404 not found", 5),
                (r"500 internal server error", 9),
                (r"502 bad gateway", 9),
                (r"503 service unavailable", 9),
                (r"api.*key", 8),
            ]
            for pattern, sev in api_patterns:
                if re.search(pattern, error_lower):
                    error_type = ErrorType.API_ERROR
                    severity = sev
                    patterns.append(pattern)
                    break
        
        # Extract location if available
        location_patterns = [
            r"file ['\"](.+?)['\"],? line (\d+)",
            r"at .+\(([^)]+)\)",
            r"in (\w+\.py):(\d+)",
        ]
        for pattern in location_patterns:
            match = re.search(pattern, error_output)
            if match:
                location = ":".join(match.groups())
                break
        
        # Extract message
        message = error_output.strip().split('\n')[0] if error_output.strip() else "Unknown error"
        
        return ErrorDiagnosis(
            error_type=error_type,
            message=message,
            location=location,
            context=context,
            severity=severity,
            patterns=patterns
        )
    
    def get_targeted_fix(self, diagnosis: ErrorDiagnosis) -> FixStrategy:
        """
        Get a targeted fix strategy based on the error diagnosis.
        
        Args:
            diagnosis: The diagnosed error information
            
        Returns:
            FixStrategy with commands and confidence
        """
        error_type = diagnosis.error_type
        
        # Check for learned patterns first
        if self.enable_learning and error_type in self.error_patterns:
            strategies = self.error_patterns[error_type]
            if strategies:
                # Return most successful pattern
                return max(strategies, key=lambda s: s.confidence)
        
        # Define fix strategies by error type
        if error_type == ErrorType.IMPORT_ERROR:
            missing_module = diagnosis.context.get("missing_module")
            if missing_module:
                return FixStrategy(
                    strategy_type="install_dependency",
                    description=f"Install missing module: {missing_module}",
                    commands=[
                        f"pip install {missing_module}",
                        f"pip install {missing_module} --upgrade"
                    ],
                    confidence=0.9,
                    prerequisites=["pip available"],
                    side_effects=["May install outdated version"]
                )
            return FixStrategy(
                strategy_type="install_all_deps",
                description="Install all project dependencies",
                commands=["pip install -r requirements.txt", "pip install -e ."],
                confidence=0.6
            )
        
        elif error_type == ErrorType.SYNTAX_ERROR:
            return FixStrategy(
                strategy_type="syntax_review",
                description="Syntax error detected - manual review required",
                commands=[],
                confidence=0.0,
                side_effects=["Cannot auto-fix syntax errors"]
            )
        
        elif error_type == ErrorType.TYPE_ERROR:
            return FixStrategy(
                strategy_type="type_fix",
                description="Type error detected - check type conversions",
                commands=[
                    "python -m py_compile",
                    "mypy" if _check_command("mypy") else None
                ],
                confidence=0.4,
                prerequisites=["Python type hints"]
            )
        
        elif error_type == ErrorType.ASSERTION_ERROR:
            return FixStrategy(
                strategy_type="assertion_review",
                description="Assertion failed - verify expected conditions",
                commands=["pytest -v"],
                confidence=0.5,
                prerequisites=["Tests defined"]
            )
        
        elif error_type == ErrorType.TIMEOUT:
            return FixStrategy(
                strategy_type="timeout_increase",
                description="Timeout error - increase timeout or optimize",
                commands=[
                    "export PYTHON_TIMEOUT=300",
                    "ulimit -v unlimited"
                ],
                confidence=0.6,
                side_effects=["May mask performance issues"]
            )
        
        elif error_type == ErrorType.PERMISSION_ERROR:
            location = diagnosis.location or ""
            return FixStrategy(
                strategy_type="fix_permissions",
                description=f"Fix file permissions for {location}",
                commands=[
                    f"chmod +x {location}" if location else None,
                    "sudo chown -R $USER:$USER ."
                ],
                confidence=0.8,
                side_effects=["Changes file ownership"]
            )
        
        elif error_type == ErrorType.API_ERROR:
            if "rate limit" in diagnosis.message.lower():
                return FixStrategy(
                    strategy_type="rate_limit_wait",
                    description="Rate limited - wait and retry",
                    commands=["sleep 60"],
                    confidence=0.7,
                    side_effects=["Adds delay"]
                )
            return FixStrategy(
                strategy_type="api_config_review",
                description="API error - review configuration",
                commands=[".env check", "API_KEY validation"],
                confidence=0.5
            )
        
        else:
            return FixStrategy(
                strategy_type="general_troubleshoot",
                description="Unknown error - general troubleshooting",
                commands=["pip install --upgrade pip", "python -m pip install --upgrade setuptools"],
                confidence=0.3
            )
    
    def apply_and_verify(
        self,
        fix: FixStrategy,
        test_fn: Optional[Callable[[], bool]] = None,
        apply_fn: Optional[Callable[[str], bool]] = None
    ) -> bool:
        """
        Apply a fix and verify it works.
        
        Args:
            fix: The fix strategy to apply
            test_fn: Optional function to test if fix works
            
        Returns:
            True if fix was successful, False otherwise
        """
        if not fix.commands:
            return False
        
        # Try each command in the fix strategy
        for command in fix.commands:
            if not command:
                continue
                
            print(f"   🔧 Applying: {command}")
            
            if apply_fn:
                success = apply_fn(command)
            else:
                # Default: run command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                success = result.returncode == 0
                
                if not success:
                    print(f"      ❌ Command failed: {result.stderr[:100]}")
            
            if success:
                print(f"      ✅ Command succeeded")
                
                # Verify with test function if provided
                if test_fn:
                    print(f"   🔍 Verifying with test function...")
                    if test_fn():
                        print(f"      ✅ Verification passed")
                        return True
                    else:
                        print(f"      ❌ Verification failed")
                        continue
                else:
                    return True
        
        return False
    
    def escalate(self, all_attempts: List[Tuple[ErrorDiagnosis, FixStrategy, bool]]) -> str:
        """
        Generate escalation message when all automated fixes have failed.
        
        Args:
            all_attempts: List of (diagnosis, fix, success) tuples
            
        Returns:
            Escalation message with diagnostic information
        """
        failed_diagnoses = [d for d, _, success in all_attempts if not success]
        
        if not failed_diagnoses:
            return "No failed attempts to escalate"
        
        # Group by error type
        error_counts: Dict[ErrorType, int] = {}
        for diag in failed_diagnoses:
            error_counts[diag.error_type] = error_counts.get(diag.error_type, 0) + 1
        
        most_common = max(error_counts, key=error_counts.get)
        
        # Generate escalation message
        escalation = [
            "=" * 50,
            "ESCALATION: Manual intervention required",
            "=" * 50,
            f"Total failed attempts: {len(all_attempts)}",
            f"Most common error: {most_common.value}",
            f"Severity: {failed_diagnoses[0].severity}/10",
            "",
            "Failed error types:",
        ]
        
        for error_type, count in sorted(error_counts.items(), key=lambda x: -x[1]):
            escalation.append(f"  - {error_type.value}: {count} occurrence(s)")
        
        if failed_diagnoses[0].location:
            escalation.append(f"\nError locations: {failed_diagnoses[0].location}")
        
        escalation.extend([
            "",
            "Last error message:",
            failed_diagnoses[-1].message[:200],
            "=" * 50,
        ])
        
        return "\n".join(escalation)
    
    def record_fix_attempt(
        self,
        diagnosis: ErrorDiagnosis,
        fix: FixStrategy,
        success: bool
    ):
        """
        Record a fix attempt for learning.
        
        Args:
            diagnosis: The error diagnosis
            fix: The fix strategy used
            success: Whether the fix worked
        """
        self.fix_history.append((diagnosis, fix, success))
        
        # Learn from successful fixes
        if success and self.enable_learning:
            error_type = diagnosis.error_type
            if error_type not in self.error_patterns:
                self.error_patterns[error_type] = []
            
            # Update confidence based on success
            fix.confidence = min(1.0, fix.confidence + 0.1)
            
            # Add to patterns if not already present
            existing = [s.description for s in self.error_patterns[error_type]]
            if fix.description not in existing:
                self.error_patterns[error_type].append(fix)


def _check_command(cmd: str) -> bool:
    """Check if a command is available."""
    result = subprocess.run(f"which {cmd}", shell=True, capture_output=True)
    return result.returncode == 0


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