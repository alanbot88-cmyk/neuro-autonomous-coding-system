"""
Test Runner - Execute tests to validate fixes
Critical for achieving high SWE-bench scores
"""

import os
import subprocess
import json
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    """Result of a test run."""
    name: str
    passed: bool
    duration_ms: float
    stdout: str
    stderr: str
    exit_code: int
    error_message: Optional[str] = None


@dataclass
class TestSuiteResult:
    """Result of a test suite run."""
    name: str
    total: int
    passed: int
    failed: int
    skipped: int
    tests: List[TestResult]
    duration_ms: float
    exit_code: int
    all_passed: bool


class TestRunner:
    """
    Executes tests to validate fixes.
    Part of the test-first validation pipeline.
    """
    
    def __init__(self, working_dir: Optional[str] = None):
        self.working_dir = working_dir or os.getcwd()
        self.test_cache: Dict[str, TestResult] = {}
        self.last_run: Optional[TestSuiteResult] = None
    
    def discover_tests(
        self,
        test_dir: Optional[str] = None,
        pattern: str = "test_*.py",
    ) -> List[str]:
        """
        Discover test files in a directory.
        
        Args:
            test_dir: Directory to search (default: current dir)
            pattern: Glob pattern for test files
            
        Returns:
            List of test file paths
        """
        test_dir = test_dir or self.working_dir
        tests = []
        
        for root, dirs, files in os.walk(test_dir):
            # Skip common non-test directories
            dirs[:] = [d for d in dirs if d not in [
                '__pycache__', '.git', 'node_modules', '.venv', 'venv'
            ]]
            
            for f in files:
                if f.endswith('.py') and ('test' in f.lower() or pattern.replace('*', '') in f):
                    tests.append(os.path.join(root, f))
        
        return tests
    
    def run_pytest(
        self,
        test_path: Optional[str] = None,
        test_args: Optional[List[str]] = None,
        timeout: int = 300,
    ) -> TestSuiteResult:
        """
        Run pytest on a test file or directory.
        
        Args:
            test_path: Path to test file or directory
            test_args: Additional pytest arguments
            timeout: Test timeout in seconds
            
        Returns:
            TestSuiteResult with all test results
        """
        start_time = os.times().elapsed * 1000
        
        cmd = ["pytest", "-v", "--tb=short", "--no-header"]
        
        if test_args:
            cmd.extend(test_args)
        
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append(".")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            duration = os.times().elapsed * 1000 - start_time
            
            # Parse pytest output
            tests = self._parse_pytest_output(result.stdout + result.stderr)
            passed = sum(1 for t in tests if t.passed)
            failed = sum(1 for t in tests if not t.passed)
            
            suite_result = TestSuiteResult(
                name=test_path or "all tests",
                total=len(tests),
                passed=passed,
                failed=failed,
                skipped=0,
                tests=tests,
                duration_ms=duration,
                exit_code=result.returncode,
                all_passed=failed == 0 and passed > 0,
            )
            
            self.last_run = suite_result
            return suite_result
            
        except subprocess.TimeoutExpired:
            return TestSuiteResult(
                name=test_path or "all tests",
                total=0,
                passed=0,
                failed=0,
                skipped=0,
                tests=[],
                duration_ms=timeout * 1000,
                exit_code=124,
                all_passed=False,
            )
        except Exception as e:
            return TestSuiteResult(
                name=test_path or "all tests",
                total=0,
                passed=0,
                failed=1,
                skipped=0,
                tests=[TestResult(
                    name="setup",
                    passed=False,
                    duration_ms=0,
                    stdout="",
                    stderr=str(e),
                    exit_code=1,
                    error_message=str(e),
                )],
                duration_ms=0,
                exit_code=1,
                all_passed=False,
            )
    
    def run_single_test(
        self,
        test_file: str,
        test_name: str,
        timeout: int = 60,
    ) -> TestResult:
        """
        Run a single test by name.
        
        Args:
            test_file: Path to test file
            test_name: Name of test function
            timeout: Timeout in seconds
            
        Returns:
            TestResult for the single test
        """
        start_time = os.times().elapsed * 1000
        
        cmd = ["pytest", "-v", "-k", test_name, test_file]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            duration = os.times().elapsed * 1000 - start_time
            
            tests = self._parse_pytest_output(result.stdout + result.stderr)
            
            if tests:
                return tests[0]
            
            return TestResult(
                name=test_name,
                passed=result.returncode == 0,
                duration_ms=duration,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                name=test_name,
                passed=False,
                duration_ms=timeout * 1000,
                stdout="",
                stderr="Test timeout",
                exit_code=124,
                error_message="Test timed out",
            )
    
    def run_with_coverage(
        self,
        test_path: Optional[str] = None,
        coverage_output: Optional[str] = None,
    ) -> Tuple[TestSuiteResult, Dict[str, Any]]:
        """
        Run tests with coverage reporting.
        
        Returns:
            Tuple of (TestSuiteResult, coverage_data)
        """
        coverage_output = coverage_output or tempfile.mktemp(suffix=".json")
        
        cmd = [
            "pytest",
            "-v",
            "--cov",
            "--cov-report=json",
            f"--cov-report=json:{coverage_output}",
            "--cov-branch",
        ]
        
        if test_path:
            cmd.append(test_path)
        
        result = self.run_pytest()
        
        # Load coverage data
        coverage_data = {}
        if os.path.exists(coverage_output):
            try:
                with open(coverage_output, 'r') as f:
                    coverage_data = json.load(f)
            except:
                pass
        
        return result, coverage_data
    
    def _parse_pytest_output(self, output: str) -> List[TestResult]:
        """Parse pytest output into TestResult objects."""
        tests = []
        lines = output.split('\n')
        
        current_test = None
        
        for line in lines:
            if '::test_' in line or '::' in line:
                # New test line
                parts = line.split('::')
                if len(parts) >= 2:
                    name = parts[-1].split(' ')[0]
                    passed = 'PASSED' in line or '✓' in line
                    failed = 'FAILED' in line or '✗' in line
                    
                    current_test = TestResult(
                        name=name,
                        passed=passed,
                        duration_ms=0,
                        stdout="",
                        stderr="",
                        exit_code=0 if passed else 1,
                    )
            
            elif current_test:
                if 'PASSED' in line:
                    current_test.passed = True
                    current_test.exit_code = 0
                    tests.append(current_test)
                    current_test = None
                elif 'FAILED' in line:
                    current_test.passed = False
                    current_test.exit_code = 1
                    tests.append(current_test)
                    current_test = None
                elif 'ERROR' in line:
                    current_test.passed = False
                    current_test.exit_code = 1
                    current_test.error_message = line
                    tests.append(current_test)
                    current_test = None
        
        return tests
    
    def get_failed_tests(self) -> List[str]:
        """Get list of failed test names from last run."""
        if not self.last_run:
            return []
        return [t.name for t in self.last_run.tests if not t.passed]
    
    def get_passing_tests(self) -> List[str]:
        """Get list of passing test names from last run."""
        if not self.last_run:
            return []
        return [t.name for t in self.last_run.tests if t.passed]
    
    def format_summary(self) -> str:
        """Format a human-readable summary of last run."""
        if not self.last_run:
            return "No tests run yet"
        
        r = self.last_run
        summary = f"Test Summary: {r.name}\n"
        summary += f"  Total: {r.total}\n"
        summary += f"  Passed: {r.passed} ✓\n"
        summary += f"  Failed: {r.failed} ✗\n"
        summary += f"  Duration: {r.duration_ms/1000:.1f}s\n"
        summary += f"  Status: {'ALL PASSED' if r.all_passed else 'SOME FAILED'}\n"
        
        if r.failed > 0:
            summary += "\nFailed tests:\n"
            for t in r.tests:
                if not t.passed:
                    summary += f"  - {t.name}\n"
                    if t.error_message:
                        summary += f"    {t.error_message[:100]}\n"
        
        return summary


# Convenience functions
def run_tests(working_dir: Optional[str] = None, test_path: Optional[str] = None) -> TestSuiteResult:
    """
    Quick function to run tests.
    
    Usage:
        from neuro.validation.test_runner import run_tests
        
        result = run_tests("/path/to/project", "tests/")
        if result.all_passed:
            print("All tests passed!")
    """
    runner = TestRunner(working_dir)
    return runner.run_pytest(test_path)


def quick_test(code: str, expected_output: str) -> Dict[str, Any]:
    """
    Quick inline test execution.
    
    Usage:
        from neuro.validation.test_runner import quick_test
        
        result = quick_test("print(1+1)", "2")
        print(result["passed"])  # True
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            ["python", temp_file],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        passed = result.stdout.strip() == expected_output.strip()
        
        return {
            "passed": passed,
            "expected": expected_output,
            "actual": result.stdout.strip(),
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    finally:
        os.unlink(temp_file)
