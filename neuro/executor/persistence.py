"""
Persistence Engine
===================
Manages task completion, alternative approaches, and progress tracking.

Handles:
- Goal drift detection
- Alternative strategy generation
- Blocker handling
- Progress logging
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(Enum):
    """Task completion status."""
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"
    DRIFTED = "drifted"


@dataclass
class ProgressEntry:
    """A single progress log entry."""
    step: int
    total: int
    description: str
    timestamp: float = field(default_factory=time.time)
    status: str = "pending"


@dataclass
class AlternativeApproach:
    """Alternative approach for retry."""
    approach_name: str
    strategy: str
    expected_outcome: str
    attempt: int


class PersistenceEngine:
    """
    Persistence Engine
    ==================
    Ensures tasks are properly completed with proper tracking.
    
    Attributes:
        MAX_ALTERNATIVE_APPROACHES: Maximum alternative strategies to try
        GOAL_RECHECK_EVERY_N_STEPS: Steps between goal drift checks
    """
    
    MAX_ALTERNATIVE_APPROACHES = 3
    GOAL_RECHECK_EVERY_N_STEPS = 5
    
    def __init__(self):
        """Initialize persistence engine."""
        self.progress_log: List[ProgressEntry] = []
        self.alternative_approaches: List[AlternativeApproach] = []
        self.current_step = 0
        self.goal_drift_threshold = 0.3  # 30% drift = concern
        self._original_task: Optional[Dict[str, Any]] = None
    
    def should_continue(self, state: Dict[str, Any]) -> bool:
        """
        Check if task should continue or is genuinely complete.
        
        Args:
            state: Current task state dictionary
            
        Returns:
            True if task should continue, False if complete
        """
        # Check explicit completion flags
        if state.get("complete") or state.get("done"):
            return False
        
        # Check status
        status = state.get("status", "")
        if status in [TaskStatus.COMPLETE.value, TaskStatus.FAILED.value]:
            return False
        
        # Check if tests pass (if applicable)
        test_results = state.get("test_results", {})
        if test_results:
            passed = test_results.get("passed", 0)
            failed = test_results.get("failed", 0)
            if failed == 0 and passed > 0:
                # Tests pass - check for work remaining
                if not self._has_pending_work(state):
                    return False
        
        # Check confidence score
        confidence = state.get("confidence", 0)
        task_type = state.get("task_type", "general")
        if confidence >= self._get_threshold(task_type):
            # High confidence - verify we're done
            if not self._has_pending_work(state):
                return False
        
        return True
    
    def get_alternative_approach(
        self,
        failed_approach: Dict[str, Any],
        error: str,
        attempt: int
    ) -> Optional[AlternativeApproach]:
        """
        Generate an alternative approach after failure.
        
        Args:
            failed_approach: Description of what failed
            error: Error message or description
            attempt: Current attempt number
            
        Returns:
            AlternativeApproach or None if max attempts reached
        """
        if attempt >= self.MAX_ALTERNATIVE_APPROACHES:
            return None
        
        # Analyze error type
        error_type = self._classify_error(error)
        
        # Generate alternative strategies based on error type
        strategies = {
            "syntax": [
                ("simplify_code", "Write simpler code without complex constructs"),
                ("add_types", "Add type annotations to clarify intent"),
                ("use_stdlib", "Use more standard library functions")
            ],
            "logic": [
                ("break_down", "Break complex logic into smaller steps"),
                ("add_invariants", "Add assertions and invariants"),
                ("test_incrementally", "Test each step incrementally")
            ],
            "import": [
                ("check_dependencies", "Verify all dependencies are installed"),
                ("use_alternatives", "Use alternative modules/imports"),
                ("lazy_import", "Use lazy imports for heavy dependencies")
            ],
            "timeout": [
                ("optimize_algorithm", "Optimize algorithm complexity"),
                ("chunk_processing", "Process data in smaller chunks"),
                ("add_caching", "Add caching for repeated operations")
            ],
            "api": [
                ("check_signature", "Verify function/method signature"),
                ("update_params", "Update parameters to match expected format"),
                ("use_wrapped_api", "Use wrapped API with fallback")
            ],
            "unknown": [
                ("debug_incrementally", "Debug incrementally with print statements"),
                ("isolate_component", "Isolate problematic component"),
                ("search_similar", "Search for similar solutions in codebase")
            ]
        }
        
        strategy_list = strategies.get(error_type, strategies["unknown"])
        
        # Pick strategy based on attempt number
        strategy_index = min(attempt, len(strategy_list) - 1)
        strategy_name, strategy_desc = strategy_list[strategy_index]
        
        approach = AlternativeApproach(
            approach_name=f"attempt_{attempt + 1}_{strategy_name}",
            strategy=strategy_desc,
            expected_outcome=self._describe_expected_outcome(strategy_name),
            attempt=attempt + 1
        )
        
        self.alternative_approaches.append(approach)
        
        return approach
    
    def recheck_goal(
        self,
        original_task: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> Tuple[bool, float, str]:
        """
        Detect if task has drifted from original goal.
        
        Args:
            original_task: Original task specification
            current_state: Current state of task execution
            
        Returns:
            Tuple of (has_drifted, drift_percentage, reason)
        """
        self._original_task = original_task
        
        # Extract key elements
        original_description = original_task.get("description", "").lower()
        original_type = original_task.get("type", "general")
        original_scope = set(original_task.get("scope_files", []))
        
        # What we've accomplished
        current_description = current_state.get("description", "").lower()
        current_scope = set(current_state.get("modified_files", []))
        current_results = current_state.get("results", {})
        
        # Calculate drift components
        drift_scores = []
        
        # 1. Type drift (is this still the same type of task?)
        current_type = current_state.get("task_type", original_type)
        type_match = self._calculate_type_similarity(original_type, current_type)
        drift_scores.append(("type", 1 - type_match))
        
        # 2. Scope drift (are we touching similar files?)
        if original_scope:
            scope_overlap = len(original_scope & current_scope) / len(original_scope)
            drift_scores.append(("scope", 1 - scope_overlap))
        
        # 3. Goal drift (are we addressing the same description?)
        goal_similarity = self._calculate_text_similarity(
            original_description,
            current_description
        )
        drift_scores.append(("goal", 1 - goal_similarity))
        
        # 4. Result completeness
        expected_results = original_task.get("expected_results", [])
        if expected_results:
            results_count = len([r for r in current_results.values() if r])
            completeness = results_count / len(expected_results)
            drift_scores.append(("results", 1 - completeness))
        
        # Calculate overall drift
        total_drift = sum(score for _, score in drift_scores) / len(drift_scores)
        
        has_drifted = total_drift > self.goal_drift_threshold
        
        # Generate reason
        if drift_scores:
            max_drift_component = max(drift_scores, key=lambda x: x[1])
            reason = f"Drift detected in {max_drift_component[0]} component"
        else:
            reason = "No significant drift"
        
        return has_drifted, total_drift, reason
    
    def handle_blocker(
        self,
        blocker_description: str,
        current_approach: Dict[str, Any],
        attempt: int
    ) -> Dict[str, Any]:
        """
        Handle a blocker by trying alternative approaches.
        
        Args:
            blocker_description: Description of what's blocked
            current_approach: Current approach that's blocked
            attempt: Current attempt number
            
        Returns:
            Dictionary with alternatives and recommendations
        """
        # Classify blocker
        blocker_type = self._classify_blocker(blocker_description)
        
        # Generate alternatives based on blocker type
        alternatives = []
        
        if blocker_type == "file_not_found":
            alternatives.extend([
                {
                    "action": "search_file",
                    "description": "Search for the file in the codebase",
                    "priority": 1
                },
                {
                    "action": "check_spelling",
                    "description": "Check for typos in the path",
                    "priority": 2
                },
                {
                    "action": "create_file",
                    "description": "Create the file if it should exist",
                    "priority": 3
                }
            ])
            
        elif blocker_type == "dependency_missing":
            alternatives.extend([
                {
                    "action": "install_dependency",
                    "description": "Install the missing dependency",
                    "priority": 1
                },
                {
                    "action": "use_alternative",
                    "description": "Use an alternative dependency",
                    "priority": 2
                },
                {
                    "action": "mock_dependency",
                    "description": "Mock the dependency for testing",
                    "priority": 3
                }
            ])
            
        elif blocker_type == "permission_denied":
            alternatives.extend([
                {
                    "action": "check_permissions",
                    "description": "Check file/directory permissions",
                    "priority": 1
                },
                {
                    "action": "run_as_admin",
                    "description": "Run with elevated permissions",
                    "priority": 2
                },
                {
                    "action": "change_location",
                    "description": "Use a writable location",
                    "priority": 3
                }
            ])
            
        elif blocker_type == "time_out":
            alternatives.extend([
                {
                    "action": "increase_timeout",
                    "description": "Increase operation timeout",
                    "priority": 1
                },
                {
                    "action": "optimize_operation",
                    "description": "Optimize the operation for speed",
                    "priority": 2
                },
                {
                    "action": "break_operation",
                    "description": "Break operation into smaller parts",
                    "priority": 3
                }
            ])
            
        else:  # unknown
            alternatives.extend([
                {
                    "action": "debug",
                    "description": "Add debugging to understand the blocker",
                    "priority": 1
                },
                {
                    "action": "search_documentation",
                    "description": "Search documentation for solutions",
                    "priority": 2
                },
                {
                    "action": "ask_for_help",
                    "description": "Document blocker for human review",
                    "priority": 3
                }
            ])
        
        # Sort by priority
        alternatives.sort(key=lambda x: x["priority"])
        
        return {
            "blocker_type": blocker_type,
            "alternatives": alternatives,
            "recommended": alternatives[0] if alternatives else None,
            "blocked": True
        }
    
    def log_progress(
        self,
        step: int,
        total: int,
        description: str
    ) -> ProgressEntry:
        """
        Log progress of current task.
        
        Args:
            step: Current step number
            total: Total steps expected
            description: Description of current step
            
        Returns:
            ProgressEntry that was logged
        """
        entry = ProgressEntry(
            step=step,
            total=total,
            description=description
        )
        
        self.progress_log.append(entry)
        self.current_step = step
        
        return entry
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of task execution.
        
        Returns:
            Dictionary with execution summary
        """
        if not self.progress_log:
            return {
                "total_steps": 0,
                "completed_steps": 0,
                "progress_percent": 0,
                "alternative_approaches_tried": len(self.alternative_approaches),
                "status": "not_started"
            }
        
        completed = len([e for e in self.progress_log if e.status == "completed"])
        total_steps = self.progress_log[-1].total if self.progress_log else 0
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed,
            "progress_percent": (completed / total_steps * 100) if total_steps > 0 else 0,
            "alternative_approaches_tried": len(self.alternative_approaches),
            "status": self._determine_status(),
            "progress_log": [
                {
                    "step": e.step,
                    "description": e.description,
                    "status": e.status
                }
                for e in self.progress_log
            ]
        }
    
    # Helper methods
    
    def _has_pending_work(self, state: Dict[str, Any]) -> bool:
        """Check if there's pending work in the state."""
        pending = state.get("pending_tasks", [])
        queued = state.get("queued_tasks", [])
        
        if pending or queued:
            return True
        
        # Check for incomplete chunks
        chunks = state.get("chunks", [])
        incomplete = [c for c in chunks if not c.get("verified", False)]
        
        return len(incomplete) > 0
    
    def _get_threshold(self, task_type: str) -> float:
        """Get confidence threshold for task type."""
        from neuro.validation.confidence import ConfidenceChecker
        checker = ConfidenceChecker()
        return checker._get_threshold(task_type)
    
    def _classify_error(self, error: str) -> str:
        """Classify error type from error message."""
        error_lower = error.lower()
        
        if any(term in error_lower for term in ["syntax", "parse", "indent"]):
            return "syntax"
        elif any(term in error_lower for term in ["logic", "assertion", "condition"]):
            return "logic"
        elif any(term in error_lower for term in ["import", "module", "no module"]):
            return "import"
        elif any(term in error_lower for term in ["timeout", "timed out"]):
            return "timeout"
        elif any(term in error_lower for term in ["api", "parameter", "argument"]):
            return "api"
        else:
            return "unknown"
    
    def _describe_expected_outcome(self, strategy: str) -> str:
        """Describe expected outcome for a strategy."""
        outcomes = {
            "simplify_code": "Cleaner code that is easier to debug",
            "add_types": "Clearer type information for better inference",
            "use_stdlib": "More reliable code using standard library",
            "break_down": "Modular code with clear separation of concerns",
            "add_invariants": "Self-documenting code with runtime checks",
            "test_incrementally": "Verified working state at each step",
            "check_dependencies": "All required dependencies present and importable",
            "use_alternatives": "Working code using available libraries",
            "lazy_import": "Fast startup with deferred heavy imports",
            "optimize_algorithm": "Faster code with better complexity",
            "chunk_processing": "Lower memory usage with streaming processing",
            "add_caching": "Faster repeated operations with cache",
            "check_signature": "Correct function calls matching definitions",
            "update_params": "Valid parameters for called functions",
            "use_wrapped_api": "Reliable API calls with proper error handling",
            "debug_incrementally": "Identified root cause of the issue",
            "isolate_component": "Isolated problematic component for focused fix",
            "search_similar": "Found examples of working similar code"
        }
        return outcomes.get(strategy, "Improved code implementation")
    
    def _classify_blocker(self, description: str) -> str:
        """Classify blocker type."""
        desc_lower = description.lower()
        
        if any(term in desc_lower for term in ["not found", "no such file", "exists"]):
            return "file_not_found"
        elif any(term in desc_lower for term in ["import", "module", "no module", "dependency"]):
            return "dependency_missing"
        elif any(term in desc_lower for term in ["permission", "access denied", "readonly"]):
            return "permission_denied"
        elif any(term in desc_lower for term in ["timeout", "timed out", "too long"]):
            return "time_out"
        else:
            return "unknown"
    
    def _calculate_type_similarity(self, type1: str, type2: str) -> float:
        """Calculate similarity between task types."""
        # Identical types
        if type1 == type2:
            return 1.0
        
        # Related types
        related_groups = [
            {"code_fix", "debugging", "bug_detection"},
            {"new_feature", "code_generation", "api_development"},
            {"refactor", "refactoring", "code_review"},
            {"research", "data_analysis"}
        ]
        
        for group in related_groups:
            if type1 in group and type2 in group:
                return 0.8
        
        return 0.3  # Unrelated types
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity."""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _determine_status(self) -> str:
        """Determine overall status of the task."""
        if not self.progress_log:
            return "not_started"
        
        last_entry = self.progress_log[-1]
        
        if last_entry.status == "completed":
            return "completed"
        elif last_entry.status == "failed":
            return "failed"
        else:
            return "in_progress"


class TaskPersistence:
    """
    Simple task persistence for resume capability.
    
    Allows saving and loading task state for resume after interruption.
    """
    
    def __init__(self, storage_path: str = ".neuro/persistence"):
        """
        Initialize task persistence.
        
        Args:
            storage_path: Path to store persistence files
        """
        self.storage_path = storage_path
        self._ensure_storage_path()
    
    def _ensure_storage_path(self) -> None:
        """Ensure storage directory exists."""
        import os
        os.makedirs(self.storage_path, exist_ok=True)
    
    def save_state(self, task_id: str, state: Dict[str, Any]) -> bool:
        """
        Save task state for resume.
        
        Args:
            task_id: Unique task identifier
            state: Task state to save
            
        Returns:
            True if save successful
        """
        import json
        import os
        
        try:
            path = os.path.join(self.storage_path, f"{task_id}.json")
            with open(path, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception:
            return False
    
    def load_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Load saved task state.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            Saved state or None if not found
        """
        import json
        import os
        
        try:
            path = os.path.join(self.storage_path, f"{task_id}.json")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return None
    
    def delete_state(self, task_id: str) -> bool:
        """
        Delete saved task state.
        
        Args:
            task_id: Unique task identifier
            
        Returns:
            True if delete successful
        """
        import os
        
        try:
            path = os.path.join(self.storage_path, f"{task_id}.json")
            if os.path.exists(path):
                os.remove(path)
            return True
        except Exception:
            return False
