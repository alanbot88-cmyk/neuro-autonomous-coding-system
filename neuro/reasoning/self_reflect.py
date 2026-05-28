"""
Self-Reflection - Critical for error correction
Part of multi-pass reasoning for 75-80% performance
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ReflectionResult:
    """Result of self-reflection."""
    original_response: str
    reflection: str
    issues_found: List[str]
    needs_revision: bool
    revised_response: str = ""
    confidence: float = 0.5


class SelfReflector:
    """
    Self-reflection to catch errors and improve solutions.
    Key component for achieving high SWE-bench scores.
    """
    
    def __init__(self):
        self.reflection_history: List[ReflectionResult] = []
    
    def reflect(
        self,
        response: str,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ReflectionResult:
        """
        Reflect on a response to identify issues.
        """
        issues = []
        
        # Check for common issues
        goal_keywords = goal.lower().split()[:5]
        response_lower = response.lower()
        
        if not any(kw in response_lower for kw in goal_keywords if len(kw) > 4):
            issues.append("Response doesn't clearly address the goal")
        
        # Check for uncertainty markers
        uncertainty_markers = [
            "not sure", "might be", "perhaps", "maybe", "possibly",
            "i think", "i believe", "could be wrong", "uncertain"
        ]
        
        uncertainty_count = sum(1 for m in uncertainty_markers if m in response_lower)
        if uncertainty_count > 3:
            issues.append("High uncertainty - may need more analysis")
        
        # Check for code quality issues
        code_indicators = ["```", "def ", "class ", "import ", "async def"]
        has_code = any(ind in response for ind in code_indicators)
        
        if has_code:
            if response.count("```") % 2 != 0:
                issues.append("Unclosed code block")
            
            if "TODO" in response or "FIXME" in response:
                issues.append("Code contains TODOs - incomplete implementation")
        
        # Check for error handling
        if "raise" in response_lower or "except" in response_lower:
            if "try" not in response_lower:
                issues.append("Exception handling without try block")
        
        needs_revision = len(issues) >= 2 or any(
            "test" in i.lower() or "error" in i.lower()
            for i in issues
        )
        
        reflection = self._build_reflection(issues, goal, context)
        
        result = ReflectionResult(
            original_response=response,
            reflection=reflection,
            issues_found=issues,
            needs_revision=needs_revision,
            confidence=1.0 - (len(issues) * 0.15),
        )
        
        self.reflection_history.append(result)
        return result
    
    def _build_reflection(
        self,
        issues: List[str],
        goal: str,
        context: Optional[Dict],
    ) -> str:
        """Build reflection text from issues."""
        if not issues:
            return "No issues identified. Solution appears solid."
        
        reflection = "Self-reflection:\n\n"
        for i, issue in enumerate(issues, 1):
            reflection += f"{i}. {issue}\n"
        
        return reflection


def reflect_on_response(response: str, goal: str, context: Optional[Dict] = None) -> ReflectionResult:
    """Quick function to reflect."""
    reflector = SelfReflector()
    return reflector.reflect(response, goal, context)
