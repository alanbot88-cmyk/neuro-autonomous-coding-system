# Shell Executor with Self-Healing
# Executes shell commands, detects errors, auto-fixes, and validates

import subprocess
import re
import time
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class ErrorSeverity(Enum):
    SYNTAX = "syntax"       # Compilation/parsing errors
    RUNTIME = "runtime"     # Execution errors
    DEPENDENCY = "dependency"  # Missing packages/modules
    CONFIG = "config"       # Configuration errors
    PERMISSION = "permission"  # Permission denied
    NETWORK = "network"     # Network/fetch errors
    UNKNOWN = "unknown"

@dataclass
class ShellError:
    """Detected shell error."""
    severity: ErrorSeverity
    message: str
    line_hint: Optional[int] = None
    file_hint: Optional[str] = None
    suggestion: Optional[str] = None
    original_command: str = ""

@dataclass
class ExecutionResult:
    """Result of shell execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    errors: List[ShellError] = field(default_factory=list)
    fixes_attempted: List[str] = field(default_factory=list)
    validation_passed: bool = False

class ShellExecutor:
    """
    Execute shell commands with self-healing capabilities.
    Detects errors, attempts fixes, and validates success.
    
    Usage:
        from neuro.skills.shell_executor import ShellExecutor
        
        executor = ShellExecutor()
        result = executor.execute("npm install")
        
        # With auto-fix
        result = executor.execute_with_fix("python app.py", max_retries=3)
    """
    
    # Error patterns for detection
    ERROR_PATTERNS = {
        ErrorSeverity.SYNTAX: [
            (r'SyntaxError:', "Python syntax error"),
            (r'ParseError:', "JavaScript parse error"),
            (r'Error:.*unexpected token', "Unexpected token error"),
            (r'Error:.*cannot find', "Cannot find symbol"),
            (r'invalid syntax', "Invalid syntax"),
            (r'unexpected EOF', "Unexpected end of file"),
        ],
        ErrorSeverity.RUNTIME: [
            (r'Error:.*not defined', "Variable not defined"),
            (r'Error:.*is not a function', "Not a function error"),
            (r'Error:.*is not iterable', "Not iterable error"),
            (r'IndexError:', "Index out of bounds"),
            (r'KeyError:', "Key not found in dict"),
            (r'AttributeError:', "Attribute not found"),
            (r'TypeError:', "Type mismatch error"),
            (r'ZeroDivisionError:', "Division by zero"),
            (r'NullPointerException', "Null pointer"),
        ],
        ErrorSeverity.DEPENDENCY: [
            (r'No module named', "Python module not found"),
            (r'Cannot find module', "Module not found"),
            (r'No such file or directory', "File not found"),
            (r'Module not found:', "Module not installed"),
            (r'ENOENT', "Path does not exist"),
            (r'Error:.*package.json', "Missing package.json"),
            (r'Error:.*npm install', "npm install required"),
            (r'Error:.*pip install', "pip install required"),
            (r'Error:.*requires.*dependency', "Missing dependency"),
        ],
        ErrorSeverity.CONFIG: [
            (r'Error:.*config', "Configuration error"),
            (r'Error:.*invalid option', "Invalid option"),
            (r'Error:.*permission denied', "Permission issue"),
            (r'EACCES', "Access denied"),
        ],
        ErrorSeverity.PERMISSION: [
            (r'Permission denied', "Permission denied"),
            (r'EACCES', "Access denied"),
            (r'must be root', "Requires root privileges"),
        ],
        ErrorSeverity.NETWORK: [
            (r'Error:.*ECONNREFUSED', "Connection refused"),
            (r'Error:.*ETIMEDOUT', "Connection timeout"),
            (r'Error:.*ENOTFOUND', "Host not found"),
            (r'Error:.*fetch failed', "Fetch failed"),
        ],
    }
    
    # Fix strategies for different error types
    FIX_STRATEGIES = {
        ErrorSeverity.SYNTAX: [
            ("missing colon", "Add missing ':' at end of line"),
            ("missing parenthesis", "Add missing ')'"),
            ("missing quotes", "Add missing quotes"),
            ("indentation", "Fix indentation"),
        ],
        ErrorSeverity.DEPENDENCY: [
            ("pip install", "Try installing missing package"),
            ("npm install", "Try npm install"),
            ("create directory", "Create missing directory"),
            ("chmod", "Fix file permissions"),
        ],
        ErrorSeverity.CONFIG: [
            ("create config", "Create missing config file"),
            ("fix path", "Fix incorrect path"),
        ],
        ErrorSeverity.PERMISSION: [
            ("chmod +x", "Make file executable"),
            ("chmod 755", "Fix permissions"),
        ],
    }
    
    def __init__(self, working_dir: str = "."):
        self.working_dir = working_dir
        self.execution_history: List[ExecutionResult] = []
        self.fix_count = 0
    
    def execute(self, command: str, timeout: int = 120, 
                capture_output: bool = True) -> ExecutionResult:
        """
        Execute a shell command.
        
        Args:
            command: Shell command to execute
            timeout: Max execution time in seconds
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            ExecutionResult with success status and output
        """
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # Detect errors in output
            errors = self._detect_errors(
                result.stdout + result.stderr,
                command
            )
            
            execution_result = ExecutionResult(
                success=result.returncode == 0 and len(errors) == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration_ms=duration_ms,
                errors=errors
            )
            
            self.execution_history.append(execution_result)
            return execution_result
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                exit_code=-1,
                duration_ms=timeout * 1000,
                errors=[ShellError(
                    severity=ErrorSeverity.UNKNOWN,
                    message=f"Command timed out after {timeout}s",
                    original_command=command
                )]
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                duration_ms=(time.time() - start_time) * 1000,
                errors=[ShellError(
                    severity=ErrorSeverity.UNKNOWN,
                    message=str(e),
                    original_command=command
                )]
            )
    
    def execute_with_fix(self, command: str, max_retries: int = 3,
                         context: Dict = None) -> ExecutionResult:
        """
        Execute command with automatic error fixing.
        
        Args:
            command: Shell command to execute
            max_retries: Max fix attempts
            context: Additional context for fixing (project files, etc.)
            
        Returns:
            ExecutionResult with fixes applied
        """
        context = context or {}
        current_command = command
        result = self.execute(current_command)
        fixes = []
        
        iteration = 0
        while not result.success and iteration < max_retries:
            iteration += 1
            
            if not result.errors:
                # No specific errors to fix
                break
            
            # Try to fix the most severe error
            most_severe = result.errors[0]
            
            # Attempt fix based on error type
            fix_result = self._attempt_fix(most_severe, context)
            
            if fix_result:
                fixes.append(fix_result)
                self.fix_count += 1
                
                # Re-execute after fix
                result = self.execute(current_command)
            else:
                # Can't fix this error
                break
        
        result.fixes_attempted = fixes
        result.success = result.exit_code == 0 and len(result.errors) == 0
        
        return result
    
    def _detect_errors(self, output: str, command: str) -> List[ShellError]:
        """Detect errors in command output."""
        errors = []
        
        for severity, patterns in self.ERROR_PATTERNS.items():
            for pattern, description in patterns:
                matches = re.finditer(pattern, output, re.IGNORECASE)
                for match in matches:
                    # Extract line number if present
                    line_hint = self._extract_line_number(output, match.start())
                    file_hint = self._extract_file_path(output, match.start())
                    
                    error = ShellError(
                        severity=severity,
                        message=match.group(0),
                        line_hint=line_hint,
                        file_hint=file_hint,
                        suggestion=self._generate_suggestion(severity, match.group(0)),
                        original_command=command
                    )
                    errors.append(error)
        
        return errors
    
    def _extract_line_number(self, output: str, match_pos: int) -> Optional[int]:
        """Extract line number from error message."""
        # Look for line number patterns like "line 42" or "Line 42:"
        text_before = output[:match_pos]
        lines_before = text_before.count('\n') + 1
        
        # Also check for explicit line number in text
        match = re.search(r'line (\d+)', output[match_pos:match_pos+100], re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return lines_before if lines_before > 0 else None
    
    def _extract_file_path(self, output: str, match_pos: int) -> Optional[str]:
        """Extract file path from error message."""
        # Look for common file path patterns
        text_window = output[max(0, match_pos-50):match_pos+100]
        
        # Match paths like /path/to/file.py or ./file.py
        match = re.search(r'[\w./-]+\.(py|js|ts|jsx|tsx|json|md)', text_window)
        if match:
            return match.group(0)
        
        # Check for "File" or "in" patterns
        match = re.search(r'(?:File |in )([\w./-]+\.\w+)', text_window)
        if match:
            return match.group(1)
        
        return None
    
    def _generate_suggestion(self, severity: ErrorSeverity, error_msg: str) -> str:
        """Generate fix suggestion based on error type."""
        suggestions = {
            ErrorSeverity.SYNTAX: "Check syntax and fix the error",
            ErrorSeverity.RUNTIME: "Check variable definitions and types",
            ErrorSeverity.DEPENDENCY: "Install missing dependency or check path",
            ErrorSeverity.CONFIG: "Check configuration file",
            ErrorSeverity.PERMISSION: "Fix file permissions with chmod",
            ErrorSeverity.NETWORK: "Check network connection",
            ErrorSeverity.UNKNOWN: "Review error message and fix",
        }
        return suggestions.get(severity, "Review and fix error")
    
    def _attempt_fix(self, error: ShellError, 
                    context: Dict) -> Optional[str]:
        """
        Attempt to fix an error.
        Returns description of fix attempted or None if can't fix.
        """
        fix_description = None
        
        if error.severity == ErrorSeverity.DEPENDENCY:
            if "No module named" in error.message:
                # Extract module name
                match = re.search(r"No module named '(\w+)'", error.message)
                if match:
                    module = match.group(1)
                    # Try pip install
                    result = self.execute(f"pip install {module}")
                    if result.success:
                        fix_description = f"Installed {module} via pip"
                    else:
                        # Try with specific version
                        result = self.execute(f"pip install {module} --upgrade")
                        if result.success:
                            fix_description = f"Upgraded {module} via pip"
            
            elif "Cannot find module" in error.message:
                match = re.search(r"Cannot find module '(\w+)'", error.message)
                if match:
                    module = match.group(1)
                    result = self.execute(f"npm install {module}")
                    if result.success:
                        fix_description = f"Installed {module} via npm"
            
            elif "No such file or directory" in error.message:
                match = re.search(r"No such file or directory: '?([\w./-]+)'?", error.message)
                if match:
                    path = match.group(1)
                    # Try creating directory
                    if '/' in path:
                        dir_path = os.path.dirname(path)
                        self.execute(f"mkdir -p {dir_path}")
                        fix_description = f"Created directory {dir_path}"
        
        elif error.severity == ErrorSeverity.PERMISSION:
            if "Permission denied" in error.message:
                match = re.search(r"Permission denied: '?([\w./-]+)'?", error.message)
                if match:
                    file_path = match.group(1)
                    self.execute(f"chmod 755 {file_path}")
                    fix_description = f"Fixed permissions for {file_path}"
        
        elif error.severity == ErrorSeverity.SYNNTAX:
            if "missing colon" in error.message.lower():
                fix_description = "Syntax error - requires manual review"
            else:
                fix_description = "Syntax error - requires manual review"
        
        return fix_description
    
    def run_tests(self, test_command: str = "pytest",
                  coverage: bool = False) -> ExecutionResult:
        """Run project tests with optional coverage."""
        cmd = test_command
        if coverage:
            cmd += " --cov --cov-report=term-missing"
        
        result = self.execute(cmd)
        result.validation_passed = result.success and "passed" in result.stdout.lower()
        
        return result
    
    def get_history(self) -> List[Dict]:
        """Get execution history."""
        return [
            {
                "success": r.success,
                "exit_code": r.exit_code,
                "duration_ms": r.duration_ms,
                "errors": len(r.errors),
                "fixes": len(r.fixes_attempted)
            }
            for r in self.execution_history[-10:]  # Last 10
        ]


def quick_execute(command: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Quick shell execution with auto-fix.
    
    Usage:
        from neuro.skills.shell_executor import quick_execute
        
        result = quick_execute("python app.py", max_retries=3)
        print(f"Success: {result['success']}")
        print(f"Fixes: {result['fixes_attempted']}")
    """
    executor = ShellExecutor()
    result = executor.execute_with_fix(command, max_retries=max_retries)
    
    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "duration_ms": result.duration_ms,
        "errors": [e.message for e in result.errors],
        "fixes_attempted": result.fixes_attempted,
        "validation_passed": result.validation_passed
    }


# SKILL.md content
SKILL_MD = """
---
name: shell-executor
description: Execute shell commands with self-healing and auto-fix capabilities
triggers:
  - shell
  - execute
  - bash
  - command
  - run
  - fix
  - error
---

# Shell Executor with Self-Healing

Executes shell commands, detects errors, auto-fixes, and validates success.

## Features

### 1. Error Detection
Automatically detects:
- Syntax errors (Python, JavaScript, etc.)
- Runtime errors (undefined variables, type mismatches)
- Dependency errors (missing modules, packages)
- Configuration errors
- Permission issues
- Network errors

### 2. Auto-Fix
Attempts automatic fixes:
- Installs missing Python packages (pip install)
- Installs missing npm packages
- Creates missing directories
- Fixes file permissions (chmod)
- Re-executes after fixes

### 3. Validation
- Returns success/failure status
- Captures stdout/stderr
- Tracks execution time
- Records fixes attempted

## Usage

```python
from neuro.skills.shell_executor import ShellExecutor, quick_execute

# Simple execution
executor = ShellExecutor()
result = executor.execute("python app.py")

# With auto-fix (3 retries)
result = executor.execute_with_fix("python app.py", max_retries=3)

# Quick execute
result = quick_execute("pytest tests/", max_retries=3)

# Run tests with coverage
result = executor.run_tests("pytest", coverage=True)
```

## Error Types

| Severity | Examples | Fix Strategy |
|----------|----------|--------------|
| SYNTAX | SyntaxError, unexpected token | Manual review |
| RUNTIME | TypeError, AttributeError | Check types |
| DEPENDENCY | No module named | pip/npm install |
| CONFIG | Invalid option | Fix config |
| PERMISSION | EACCES | chmod |
| NETWORK | ECONNREFUSED | Check connection |
"""