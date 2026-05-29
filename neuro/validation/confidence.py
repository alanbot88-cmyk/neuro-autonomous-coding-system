"""
Confidence Threshold System
============================
Determines when to retry based on test results and task type.

Used by ValidatorAgent to decide if implementation is good enough
or needs another iteration.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ThresholdConfig:
    """Configuration for a specific task type threshold."""
    threshold: float
    retry_weight: float
    description: str


class ConfidenceChecker:
    """
    Confidence Threshold Checker
    ============================
    Calculates confidence scores and determines retry strategy.
    
    Attributes:
        THRESHOLDS: Dictionary mapping task types to confidence thresholds
    """
    
    # Confidence thresholds by task type
    # Higher threshold = higher confidence required before accepting
    THRESHOLDS: Dict[str, float] = {
        "code_fix": 0.85,      # Bug fixes need good confidence
        "new_feature": 0.80,   # New features slightly less strict
        "refactor": 0.90,      # Refactoring needs highest confidence (behavior must be preserved)
        "web_app": 0.75,       # Web apps can be more exploratory
        "research": 0.70,       # Research can be less certain
        "documentation": 0.80,  # Docs need good quality
    }
    
    # Weights for different test result factors
    TEST_WEIGHTS = {
        "pass_rate": 0.4,       # Primary weight: how many tests pass
        "test_coverage": 0.2,   # Secondary: are critical paths covered
        "new_failures": 0.3,    # Penalty for new failures introduced
        "runtime": 0.1         # Smaller weight: test execution time
    }
    
    def __init__(self, custom_thresholds: Optional[Dict[str, float]] = None):
        """
        Initialize confidence checker with optional custom thresholds.
        
        Args:
            custom_thresholds: Override default thresholds for specific task types
        """
        if custom_thresholds:
            self.THRESHOLDS = {**self.THRESHOLDS, **custom_thresholds}
    
    def calculate(self, test_results: Dict[str, Any], task_type: str) -> float:
        """
        Calculate confidence score based on test results.
        
        Args:
            test_results: Dict with 'passed', 'failed', 'skipped', 'total' counts
            task_type: Type of task ('code_fix', 'new_feature', etc.)
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not test_results:
            return 0.0
        
        # Extract test metrics
        passed = test_results.get("passed", 0)
        failed = test_results.get("failed", 0)
        skipped = test_results.get("skipped", 0)
        total = test_results.get("total", 1)
        duration = test_results.get("duration_ms", 0)
        
        # Avoid division by zero
        if total == 0:
            return 0.5
        
        # Calculate pass rate (primary factor)
        pass_rate = passed / total
        
        # Calculate test coverage score
        # More tests relative to expectations = better coverage
        expected_min = self._get_expected_tests(task_type)
        coverage_factor = min(1.0, total / max(expected_min, 1))
        
        # Calculate new failures penalty (for regression detection)
        # Higher failure rate = lower confidence
        failure_rate = failed / total
        new_failure_penalty = failure_rate * 0.5  # Up to 50% penalty for failures
        
        # Runtime factor (longer tests might indicate issues)
        runtime_penalty = self._calculate_runtime_penalty(duration, task_type)
        
        # Weighted combination
        confidence = (
            pass_rate * self.TEST_WEIGHTS["pass_rate"] +
            coverage_factor * self.TEST_WEIGHTS["test_coverage"] +
            (1.0 - new_failure_penalty) * self.TEST_WEIGHTS["new_failures"] +
            (1.0 - runtime_penalty) * self.TEST_WEIGHTS["runtime"]
        )
        
        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
    
    def should_retry(self, score: float, task_type: str) -> bool:
        """
        Determine if task should be retried based on confidence score.
        
        Args:
            score: Calculated confidence score (0.0-1.0)
            task_type: Type of task
            
        Returns:
            True if below threshold and should retry
        """
        threshold = self._get_threshold(task_type)
        return score < threshold
    
    def get_retry_instructions(
        self, 
        test_results: Dict[str, Any], 
        score: float,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate specific instructions for retry based on test results.
        
        Args:
            test_results: Test results dictionary
            score: Current confidence score
            task_type: Optional task type for context
            
        Returns:
            Dictionary with retry instructions containing:
            - priority_fixes: List of high-priority fixes
            - focus_areas: Areas that need attention
            - suggested_approach: How to approach the retry
        """
        instructions = {
            "priority_fixes": [],
            "focus_areas": [],
            "suggested_approach": "",
            "current_score": score
        }
        
        failed_tests = test_results.get("failures", [])
        passed = test_results.get("passed", 0)
        total = test_results.get("total", 1)
        
        # Analyze failures for specific guidance
        if failed_tests:
            for failure in failed_tests[:3]:  # Focus on top 3 failures
                test_name = failure.get("name", "unknown")
                error_msg = failure.get("error", "")
                
                # Categorize error type
                if "assertion" in error_msg.lower():
                    instructions["priority_fixes"].append({
                        "test": test_name,
                        "type": "assertion_failure",
                        "fix": "Review expected vs actual values in assertion"
                    })
                    instructions["focus_areas"].append(f"Fix assertion in {test_name}")
                    
                elif "import" in error_msg.lower() or "no module" in error_msg.lower():
                    instructions["priority_fixes"].append({
                        "test": test_name,
                        "type": "import_error",
                        "fix": "Check imports and dependencies"
                    })
                    instructions["focus_areas"].append("Fix import issues")
                    
                elif "timeout" in error_msg.lower():
                    instructions["priority_fixes"].append({
                        "test": test_name,
                        "type": "timeout",
                        "fix": "Optimize test or increase timeout"
                    })
                    instructions["focus_areas"].append("Fix timeout issues")
                else:
                    instructions["priority_fixes"].append({
                        "test": test_name,
                        "type": "unknown",
                        "fix": f"Analyze error: {error_msg[:100]}"
                    })
                    instructions["focus_areas"].append(f"Debug {test_name}")
        
        # Low pass rate guidance
        pass_rate = passed / total if total > 0 else 0
        if pass_rate < 0.5:
            instructions["suggested_approach"] = (
                "Low pass rate detected. Consider:\n"
                "1. Breaking implementation into smaller chunks\n"
                "2. Running implementation tests first before full test suite\n"
                "3. Adding intermediate verification points"
            )
        elif pass_rate < 0.8:
            instructions["suggested_approach"] = (
                "Partial failures present. Consider:\n"
                "1. Focus on fixing priority failures first\n"
                "2. Check for edge cases not covered\n"
                "3. Verify integration points"
            )
        else:
            instructions["suggested_approach"] = (
                "Near-threshold confidence. Consider minor adjustments:\n"
                "1. Review failing tests for false positives\n"
                "2. Add missing test coverage\n"
                "3. Improve code structure"
            )
        
        # Task-type specific guidance
        task_guidance = {
            "code_fix": "Focus on the specific bug scenario and verify edge cases",
            "new_feature": "Ensure feature integrates well with existing code",
            "refactor": "Verify behavior unchanged - run full regression suite",
            "web_app": "Test UI interactions and responsiveness",
            "research": "Cross-check findings with multiple sources",
            "documentation": "Verify accuracy against actual implementation"
        }
        
        if task_type in task_guidance:
            instructions["task_specific"] = task_guidance[task_type]
        
        return instructions
    
    def get_threshold_info(self, task_type: str) -> Dict[str, Any]:
        """
        Get detailed threshold information for a task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            Dictionary with threshold info
        """
        threshold = self._get_threshold(task_type)
        
        return {
            "task_type": task_type,
            "threshold": threshold,
            "description": self._get_threshhold_description(task_type),
            "strictness": self._get_strictness_level(threshold)
        }
    
    def _get_threshold(self, task_type: str) -> float:
        """Get threshold for task type, default to 0.80."""
        return self.THRESHOLDS.get(task_type, 0.80)
    
    def _get_expected_tests(self, task_type: str) -> int:
        """Get expected minimum number of tests for task type."""
        expectations = {
            "code_fix": 3,
            "new_feature": 5,
            "refactor": 4,
            "web_app": 4,
            "research": 1,
            "documentation": 1
        }
        return expectations.get(task_type, 3)
    
    def _calculate_runtime_penalty(self, duration_ms: int, task_type: str) -> float:
        """Calculate penalty based on test runtime."""
        # Baseline expectations by task type (in ms)
        baselines = {
            "code_fix": 5000,
            "new_feature": 10000,
            "refactor": 5000,
            "web_app": 15000
        }
        baseline = baselines.get(task_type, 5000)
        
        if duration_ms <= baseline:
            return 0.0
        
        # Progressively penalize time over baseline
        # 10% penalty per 2x baseline, max 50%
        excess_factor = duration_ms / baseline
        penalty = min(0.5, (excess_factor - 1) * 0.1)
        
        return penalty
    
    def _get_threshhold_description(self, task_type: str) -> str:
        """Get human-readable description of threshold."""
        descriptions = {
            "code_fix": "Bug fixes require 85% confidence - bugs can cause cascading issues",
            "new_feature": "New features need 80% confidence - room for iteration",
            "refactor": "Refactoring needs highest 90% confidence - must preserve behavior",
            "web_app": "Web apps at 75% confidence - more exploratory development",
            "research": "Research at 70% confidence - iterative exploration expected",
            "documentation": "Documentation at 80% confidence - accuracy important"
        }
        return descriptions.get(task_type, "Default 80% confidence threshold")
    
    def _get_strictness_level(self, threshold: float) -> str:
        """Get strictness level description."""
        if threshold >= 0.90:
            return "very strict"
        elif threshold >= 0.80:
            return "strict"
        elif threshold >= 0.70:
            return "moderate"
        else:
            return "lenient"


class ConfidenceHistory:
    """
    Tracks confidence history for pattern analysis.
    
    Used to identify:
    - Tasks that consistently fail
    - Retry patterns
    - Optimal retry strategies
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize confidence history tracker.
        
        Args:
            max_history: Maximum number of entries to track
        """
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
    
    def record(self, task_type: str, confidence_score: float, passed: bool) -> None:
        """
        Record a confidence check result.
        
        Args:
            task_type: Type of task
            confidence_score: Calculated confidence
            passed: Whether task passed threshold
        """
        entry = {
            "task_type": task_type,
            "confidence_score": confidence_score,
            "passed": passed
        }
        
        self.history.append(entry)
        
        # Trim history if needed
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_average_confidence(self, task_type: Optional[str] = None) -> float:
        """
        Get average confidence for task type or overall.
        
        Args:
            task_type: Optional filter by task type
            
        Returns:
            Average confidence score
        """
        if not self.history:
            return 0.0
        
        filtered = self.history
        if task_type:
            filtered = [e for e in self.history if e["task_type"] == task_type]
        
        if not filtered:
            return 0.0
        
        return sum(e["confidence_score"] for e in filtered) / len(filtered)
    
    def get_pass_rate(self, task_type: Optional[str] = None) -> float:
        """
        Get pass rate for task type or overall.
        
        Args:
            task_type: Optional filter by task type
            
        Returns:
            Pass rate as decimal
        """
        if not self.history:
            return 0.0
        
        filtered = self.history
        if task_type:
            filtered = [e for e in self.history if e["task_type"] == task_type]
        
        if not filtered:
            return 0.0
        
        passed = sum(1 for e in filtered if e["passed"])
        return passed / len(filtered)


def quick_confidence_check(
    test_results: Dict[str, Any],
    task_type: str
) -> tuple[float, bool, str]:
    """
    Quick confidence check for simple use cases.
    
    Args:
        test_results: Test results dictionary
        task_type: Type of task
        
    Returns:
        Tuple of (confidence_score, should_retry, message)
    """
    checker = ConfidenceChecker()
    score = checker.calculate(test_results, task_type)
    should_retry = checker.should_retry(score, task_type)
    
    threshold = checker._get_threshold(task_type)
    message = f"Confidence {score:.2f} vs threshold {threshold:.2f}"
    
    return score, should_retry, message
