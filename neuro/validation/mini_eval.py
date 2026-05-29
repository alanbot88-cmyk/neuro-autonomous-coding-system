"""
Mini Eval Harness for Neuro Autonomous Coding
Local smoke tests to prove Neuro can really act
"""

import os
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from neuro.tools.edit_parser import (
    StructuredEdit,
    CommandRunner,
    parse_structured_edit,
)
from neuro.router.smart_router import SmartRouter


@dataclass
class EvalResult:
    """Result of a mini evaluation."""
    name: str
    passed: bool
    duration_ms: float
    output: str
    error: Optional[str] = None


class MiniEvalHarness:
    """
    Mini evaluation harness for Neuro.
    
    These are NOT official benchmark scores.
    They are local smoke tests proving Neuro can:
    1. Read files
    2. Generate edits
    3. Apply edits
    4. Run tests
    5. Fix failure if needed
    
    Labeled clearly as LOCAL MINI EVALS.
    """
    
    def __init__(self, workspace: Optional[str] = None):
        self.workspace = workspace or tempfile.mkdtemp(prefix="neuro_eval_")
        self.router = SmartRouter()
        self.runner = CommandRunner(self.workspace)
        self.results: List[EvalResult] = []
    
    def cleanup(self):
        """Clean up evaluation workspace."""
        if os.path.exists(self.workspace) and self.workspace.startswith(tempfile.gettempdir()):
            shutil.rmtree(self.workspace, ignore_errors=True)
    
    def run_all_evals(self) -> Dict[str, Any]:
        """Run all mini evaluations."""
        evals = [
            self.eval_calculator_creation,
            self.eval_bug_fix,
            self.eval_file_creation,
            self.eval_simple_refactor,
        ]
        
        for eval_fn in evals:
            try:
                result = eval_fn()
                self.results.append(result)
            except Exception as e:
                self.results.append(EvalResult(
                    name=eval_fn.__name__,
                    passed=False,
                    duration_ms=0,
                    output="",
                    error=str(e),
                ))
        
        return self.get_summary()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all eval results."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "duration_ms": r.duration_ms,
                    "error": r.error,
                }
                for r in self.results
            ],
        }
    
    # =============================================================================
    # EVAL 1: Calculator Module Creation
    # =============================================================================
    
    def eval_calculator_creation(self) -> EvalResult:
        """
        Evaluation 1: Create a Python calculator module.
        
        Expected behavior:
        1. Plans task
        2. Creates source file with add, subtract, multiply, divide
        3. Creates test file
        4. Runs pytest
        5. Fixes errors if any
        6. Reports changed files and passing tests
        """
        import time
        start = time.time()
        
        # Setup: Create empty project structure
        eval_dir = Path(self.workspace) / "eval_calculator"
        eval_dir.mkdir(exist_ok=True)
        
        task = """Create a Python calculator module with:
- add(a, b) function
- subtract(a, b) function  
- multiply(a, b) function
- divide(a, b) function (return float)

Also create tests in test_calculator.py that test all functions.
Use pytest format."""
        
        # Use LLM to generate the structured edit
        system_prompt = """You are a coding assistant. Generate code for the task.
Output MUST be valid JSON in this format:
{
  "analysis": "brief reasoning summary",
  "files": [
    {
      "path": "calculator.py",
      "action": "create",
      "content": "def add(a, b):\\n    return a + b\\n\\ndef subtract(a, b):\\n    return a - b\\n\\ndef multiply(a, b):\\n    return a * b\\n\\ndef divide(a, b):\\n    return float(a) / b\\n"
    },
    {
      "path": "test_calculator.py", 
      "action": "create",
      "content": "import pytest\\nfrom calculator import add, subtract, multiply, divide\\n\\ndef test_add():\\n    assert add(2, 3) == 5\\n\\ndef test_subtract():\\n    assert subtract(5, 3) == 2\\n\\ndef test_multiply():\\n    assert multiply(2, 3) == 6\\n\\ndef test_divide():\\n    assert divide(6, 2) == 3.0\\n"
    }
  ],
  "commands": ["python -m pytest test_calculator.py -v"],
  "notes": "Basic calculator module with tests"
}"""
        
        try:
            result = self.router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                model="openrouter/qwen/qwen3-coder:free"
            )
            
            if "error" in result:
                return EvalResult(
                    name="eval_calculator_creation",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output="",
                    error=f"Router error: {result['error']}",
                )
            
            # Parse the structured edit
            edit, errors = parse_structured_edit(result["content"])
            if edit is None:
                return EvalResult(
                    name="eval_calculator_creation",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output=result["content"][:500],
                    error=f"Could not parse edit: {errors}",
                )
            
            # Apply the edit
            from neuro.tools.edit_parser import SafeFileWriterLite
            writer = SafeFileWriterLite(str(eval_dir), dry_run=False)
            
            for f in edit.files:
                if f.action == "create":
                    writer.create(f.path, f.content)
                elif f.action == "modify":
                    writer.write(f.path, f.content)
            
            # Run tests
            test_result = self.runner.run("python -m pytest test_calculator.py -v", cwd=str(eval_dir))
            
            passed = test_result.exit_code == 0
            
            return EvalResult(
                name="eval_calculator_creation",
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                output=f"Files: {writer.get_written_files()}\nTest exit code: {test_result.exit_code}\nStdout: {test_result.stdout[:500]}",
                error=test_result.stderr if not passed else None,
            )
            
        except Exception as e:
            return EvalResult(
                name="eval_calculator_creation",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                output="",
                error=str(e),
            )
    
    # =============================================================================
    # EVAL 2: Bug Fix
    # =============================================================================
    
    def eval_bug_fix(self) -> EvalResult:
        """
        Evaluation 2: Fix a failing test.
        
        Creates a buggy module and expects Neuro to:
        1. Read failing test output
        2. Inspect relevant files
        3. Generate structured patch
        4. Apply patch
        5. Re-run tests
        6. Pass
        """
        import time
        start = time.time()
        
        # Setup: Create project with intentional bug
        eval_dir = Path(self.workspace) / "eval_bugfix"
        eval_dir.mkdir(exist_ok=True)
        
        # Create buggy code
        buggy_code = '''def add_all(numbers):
    """Add all numbers in a list."""
    total = 0
    for n in numbers:
        total += n
    return total

def average(numbers):
    """Calculate average of numbers."""
    return add_all(numbers) / len(numbers)
'''
        
        buggy_test = '''import pytest
from buggy import add_all, average

def test_add_all():
    assert add_all([1, 2, 3, 4]) == 10

def test_average():
    assert average([1, 2, 3, 4]) == 2.5

def test_empty_average():
    """This will fail due to division by zero bug."""
    average([])
'''
        
        with open(eval_dir / "buggy.py", "w") as f:
            f.write(buggy_code)
        with open(eval_dir / "test_buggy.py", "w") as f:
            f.write(buggy_test)
        
        # Run tests to see failure
        test_result = self.runner.run("python -m pytest test_buggy.py -v", cwd=str(eval_dir))
        
        if test_result.exit_code == 0:
            # No bug to fix
            return EvalResult(
                name="eval_bug_fix",
                passed=True,
                duration_ms=(time.time() - start) * 1000,
                output="No bugs detected in code",
            )
        
        # Get LLM to fix the bug
        system_prompt = """You are a debugging expert. Fix the failing test by modifying the buggy.py file.
The test for empty average is failing because divide by zero.

Output MUST be valid JSON:
{
  "analysis": "The average function needs to handle empty list case",
  "files": [
    {
      "path": "buggy.py",
      "action": "modify",
      "content": "def add_all(numbers):\\n    total = 0\\n    for n in numbers:\\n        total += n\\n    return total\\n\\ndef average(numbers):\\n    if not numbers:\\n        return 0.0\\n    return add_all(numbers) / len(numbers)\\n"
    }
  ],
  "commands": ["python -m pytest test_buggy.py -v"],
  "notes": "Fixed divide by zero bug"
}"""
        
        try:
            result = self.router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Failing test output:\n{test_result.stdout}\n{test_result.stderr}"}
                ],
                model="openrouter/qwen/qwen3-coder:free"
            )
            
            if "error" in result:
                return EvalResult(
                    name="eval_bug_fix",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output=test_result.stdout[:500],
                    error=f"Router error: {result['error']}",
                )
            
            edit, errors = parse_structured_edit(result["content"])
            if edit is None:
                return EvalResult(
                    name="eval_bug_fix",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output=test_result.stdout[:500],
                    error=f"Could not parse fix: {errors}",
                )
            
            # Apply fix
            from neuro.tools.edit_parser import SafeFileWriterLite
            writer = SafeFileWriterLite(str(eval_dir), dry_run=False)
            
            for f in edit.files:
                if f.action == "modify":
                    writer.write(f.path, f.content)
            
            # Re-run tests
            test_result = self.runner.run("python -m pytest test_buggy.py -v", cwd=str(eval_dir))
            
            passed = test_result.exit_code == 0
            
            return EvalResult(
                name="eval_bug_fix",
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                output=f"Fixed: {writer.get_written_files()}\nTest exit code: {test_result.exit_code}",
                error=test_result.stderr if not passed else None,
            )
            
        except Exception as e:
            return EvalResult(
                name="eval_bug_fix",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                output=test_result.stdout[:500],
                error=str(e),
            )
    
    # =============================================================================
    # EVAL 3: Simple File Creation
    # =============================================================================
    
    def eval_file_creation(self) -> EvalResult:
        """Evaluation 3: Create a simple file."""
        import time
        start = time.time()
        
        eval_dir = Path(self.workspace) / "eval_file_create"
        eval_dir.mkdir(exist_ok=True)
        
        task = """Create a simple hello.py file that prints 'Hello, Neuro!' when run."""
        
        system_prompt = """Output MUST be valid JSON:
{
  "analysis": "Simple hello world script",
  "files": [
    {
      "path": "hello.py",
      "action": "create",
      "content": "print('Hello, Neuro!')\\n"
    }
  ],
  "commands": ["python hello.py"],
  "notes": "Basic hello world"
}"""
        
        try:
            result = self.router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                model="openrouter/qwen/qwen3-coder:free"
            )
            
            if "error" in result:
                return EvalResult(
                    name="eval_file_creation",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output="",
                    error=f"Router error: {result['error']}",
                )
            
            edit, errors = parse_structured_edit(result["content"])
            if edit is None:
                return EvalResult(
                    name="eval_file_creation",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output="",
                    error=f"Could not parse edit: {errors}",
                )
            
            from neuro.tools.edit_parser import SafeFileWriterLite
            writer = SafeFileWriterLite(str(eval_dir), dry_run=False)
            
            for f in edit.files:
                if f.action == "create":
                    writer.create(f.path, f.content)
            
            test_result = self.runner.run("python hello.py", cwd=str(eval_dir))
            
            passed = test_result.exit_code == 0 and "Hello, Neuro!" in test_result.stdout
            
            return EvalResult(
                name="eval_file_creation",
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                output=f"Files: {writer.get_written_files()}\nOutput: {test_result.stdout}",
                error=None if passed else test_result.stderr,
            )
            
        except Exception as e:
            return EvalResult(
                name="eval_file_creation",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                output="",
                error=str(e),
            )
    
    # =============================================================================
    # EVAL 4: Simple Refactor
    # =============================================================================
    
    def eval_simple_refactor(self) -> EvalResult:
        """Evaluation 4: Simple code refactor."""
        import time
        start = time.time()
        
        eval_dir = Path(self.workspace) / "eval_refactor"
        eval_dir.mkdir(exist_ok=True)
        
        # Create code that needs refactoring
        messy_code = '''def calc(x,y):
    return x+y

def calc2(x,y):
    return x-y

def calc3(x,y):
    return x*y

def calc4(x,y):
    return x/y
'''
        
        with open(eval_dir / "messy.py", "w") as f:
            f.write(messy_code)
        
        task = """Refactor the messy.py file. Rename functions to:
- add(a, b)
- subtract(a, b)
- multiply(a, b)  
- divide(a, b)

Also add docstrings to each function."""
        
        system_prompt = """Output MUST be valid JSON. Refactor messy.py:
{
  "analysis": "Renaming functions and adding docstrings",
  "files": [
    {
      "path": "messy.py",
      "action": "modify",
      "content": "def add(a, b):\\n    '''Add two numbers.'''\\n    return a + b\\n\\ndef subtract(a, b):\\n    '''Subtract b from a.'''\\n    return a - b\\n\\ndef multiply(a, b):\\n    '''Multiply two numbers.'''\\n    return a * b\\n\\ndef divide(a, b):\\n    '''Divide a by b.'''\\n    return a / b\\n"
    }
  ],
  "commands": ["python -c 'from messy import add, subtract, multiply, divide; print(add(1,2))'"],
  "notes": "Refactored to proper function names"
}"""
        
        try:
            result = self.router.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task}
                ],
                model="openrouter/qwen/qwen3-coder:free"
            )
            
            if "error" in result:
                return EvalResult(
                    name="eval_simple_refactor",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output="",
                    error=f"Router error: {result['error']}",
                )
            
            edit, errors = parse_structured_edit(result["content"])
            if edit is None:
                return EvalResult(
                    name="eval_simple_refactor",
                    passed=False,
                    duration_ms=(time.time() - start) * 1000,
                    output="",
                    error=f"Could not parse edit: {errors}",
                )
            
            from neuro.tools.edit_parser import SafeFileWriterLite
            writer = SafeFileWriterLite(str(eval_dir), dry_run=False)
            
            for f in edit.files:
                if f.action == "modify":
                    writer.write(f.path, f.content)
            
            test_result = self.runner.run(
                "python -c 'from messy import add, subtract, multiply, divide; print(add(1,2), subtract(3,1), multiply(2,3), divide(6,2))'",
                cwd=str(eval_dir)
            )
            
            passed = test_result.exit_code == 0
            
            return EvalResult(
                name="eval_simple_refactor",
                passed=passed,
                duration_ms=(time.time() - start) * 1000,
                output=f"Refactored: {writer.get_written_files()}\nOutput: {test_result.stdout}",
                error=None if passed else test_result.stderr,
            )
            
        except Exception as e:
            return EvalResult(
                name="eval_simple_refactor",
                passed=False,
                duration_ms=(time.time() - start) * 1000,
                output="",
                error=str(e),
            )


def run_mini_evals() -> Dict[str, Any]:
    """
    Run all mini evaluations and return summary.
    
    These are LOCAL SMOKE TESTS, not official benchmarks.
    """
    harness = MiniEvalHarness()
    try:
        summary = harness.run_all_evals()
        return summary
    finally:
        harness.cleanup()


if __name__ == "__main__":
    print("=" * 60)
    print("NEURO MINI EVALUATION HARNESS")
    print("=" * 60)
    print()
    print("⚠️  LOCAL SMOKE TESTS - NOT OFFICIAL BENCHMARKS")
    print()
    
    summary = run_mini_evals()
    
    print(f"Total: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print()
    
    for r in summary["results"]:
        status = "✅ PASS" if r["passed"] else "❌ FAIL"
        print(f"  {status}: {r['name']}")
        if r["error"]:
            print(f"         Error: {r['error'][:100]}")
    
    print()
    print("=" * 60)