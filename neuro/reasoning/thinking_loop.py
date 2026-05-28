"""
Multi-Pass Thinking Loop - Core for 75-80% performance
Multiple reasoning passes to converge on solution
"""

import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class PassType(Enum):
    """Types of reasoning passes."""
    ANALYSIS = "analysis"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    DEBUGGING = "debugging"
    REFLECTION = "reflection"


@dataclass
class ThinkingPass:
    """A single thinking pass."""
    pass_type: PassType
    prompt: str
    response: str = ""
    duration_ms: float = 0
    success: bool = False
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoopConfig:
    """Configuration for thinking loop."""
    max_passes: int = 4
    pass_timeout: int = 120  # seconds
    convergence_threshold: float = 0.8
    allow_stuck_detection: bool = True
    stuck_after_passes: int = 3


class ThinkingLoop:
    """
    Multi-pass thinking loop for robust problem solving.
    Key to achieving 75-80% by catching errors early.
    """
    
    def __init__(self, router, config: Optional[LoopConfig] = None):
        self.router = router
        self.config = config or LoopConfig()
        self.passes: List[ThinkingPass] = []
        self.convergence_score: float = 0.0
    
    def run(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        validate_fn: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Run multi-pass thinking loop.
        
        Args:
            goal: The task goal
            context: Optional context (code, files, errors)
            validate_fn: Optional validation function
            
        Returns:
            Dict with solution, passes, and metadata
        """
        self.passes = []
        context = context or {}
        best_solution = ""
        best_score = 0.0
        
        for pass_num in range(1, self.config.max_passes + 1):
            print(f"🔄 Pass {pass_num}/{self.config.max_passes}")
            
            # Determine pass type based on iteration
            pass_type = self._get_pass_type(pass_num, goal, context)
            
            # Create pass prompt
            prompt = self._create_pass_prompt(pass_num, pass_type, goal, context)
            
            # Execute pass
            start = time.time()
            response = self._execute_pass(prompt, context)
            duration = (time.time() - start) * 1000
            
            # Score convergence
            score = self._score_convergence(response, best_solution)
            
            # Record pass
            thinking_pass = ThinkingPass(
                pass_type=pass_type,
                prompt=prompt,
                response=response,
                duration_ms=duration,
                success=True,
                metadata={"pass_num": pass_num, "score": score}
            )
            self.passes.append(thinking_pass)
            
            # Update best solution
            if score > best_score:
                best_score = score
                best_solution = response
            
            print(f"   ✓ Pass {pass_num} complete (score: {score:.2f})")
            
            # Check convergence
            if score >= self.config.convergence_threshold:
                print(f"   🎯 Converged at pass {pass_num}!")
                break
            
            # Stuck detection
            if self.config.allow_stuck_detection and pass_num >= self.config.stuck_after_passes:
                if self._is_stuck():
                    print(f"   ⚠️ Detected stuck pattern, attempting recovery...")
                    best_solution = self._recover_from_stuck(goal, context)
                    break
            
            # Run validation if provided
            if validate_fn and pass_num >= 2:
                validation_result = validate_fn(best_solution)
                if validation_result.get("passed"):
                    print(f"   ✅ Validation passed at pass {pass_num}")
                    break
                else:
                    print(f"   ❌ Validation failed: {validation_result.get('error', 'Unknown')}")
                    context["validation_error"] = validation_result
        
        return {
            "solution": best_solution,
            "passes": [self._pass_to_dict(p) for p in self.passes],
            "num_passes": len(self.passes),
            "convergence_score": best_score,
            "total_duration_ms": sum(p.duration_ms for p in self.passes),
        }
    
    def _get_pass_type(self, pass_num: int, goal: str, context: Dict) -> PassType:
        """Determine the type of pass based on iteration."""
        if pass_num == 1:
            return PassType.ANALYSIS
        elif pass_num == 2:
            return PassType.IMPLEMENTATION
        elif pass_num == 3:
            return PassType.VALIDATION
        elif pass_num == 4:
            return PassType.DEBUGGING
        else:
            return PassType.REFLECTION
    
    def _create_pass_prompt(
        self,
        pass_num: int,
        pass_type: PassType,
        goal: str,
        context: Dict[str, Any],
    ) -> str:
        """Create the prompt for this pass WITH skill enrichment."""
        
        # Base prompt with context
        base_prompt = f"Task: {goal}\n\n"
        
        # NEW: Include active skills context
        if context.get("active_skills"):
            skills_list = ", ".join(context["active_skills"])
            base_prompt += f"🎯 Available skills: {skills_list}\n\n"
        
        if context.get("code_context"):
            base_prompt += f"Code context:\n{context['code_context'][:2000]}\n\n"
        
        if context.get("error"):
            base_prompt += f"Error message:\n{context['error']}\n\n"
        
        if context.get("validation_error"):
            base_prompt += f"Previous validation error:\n{context['validation_error']}\n\n"
        
        # NEW: Include skill hints from orchestrator
        if context.get("skill_hints"):
            base_prompt += f"Skill guidance:\n{context['skill_hints']}\n\n"
        
        # NEW: Include memory context from swarmvault
        if context.get("memory_context"):
            base_prompt += f"Relevant memory:\n{context['memory_context'][:1000]}\n\n"
        
        if self.passes and pass_num > 1:
            base_prompt += f"Previous attempts:\n"
            for i, p in enumerate(self.passes[-2:], max(1, len(self.passes) - 1)):
                base_prompt += f"Pass {i}: {p.response[:500]}...\n"
            base_prompt += "\n"
        
        # Pass-specific instructions
        if pass_type == PassType.ANALYSIS:
            return base_prompt + """
ANALYSIS PASS - Understanding the Problem

Think step by step:
1. What is the exact issue or goal?
2. What files are relevant?
3. What is the expected vs actual behavior?
4. What error messages or symptoms exist?
5. What changes are likely needed?

Provide a clear analysis and initial plan.
"""
        
        elif pass_type == PassType.IMPLEMENTATION:
            return base_prompt + """
IMPLEMENTATION PASS - Making Changes

Based on the analysis:
1. What specific code changes will you make?
2. Show the exact code changes (file paths, line numbers if possible)
3. Why will this fix the issue?
4. What could go wrong?

Be specific and concrete. Show the actual code changes.
"""
        
        elif pass_type == PassType.VALIDATION:
            return base_prompt + """
VALIDATION PASS - Verifying the Solution

Before claiming success:
1. What tests will you run to verify?
2. What is the expected output?
3. What edge cases should be checked?
4. Are there any potential regressions?

Run your verification and report actual results.
"""
        
        elif pass_type == PassType.DEBUGGING:
            return base_prompt + """
DEBUGGING PASS - Fixing Issues

If validation failed or there are issues:
1. What exactly went wrong?
2. What is the root cause?
3. How will you fix it differently?
4. What did you learn from the failure?

Provide an improved solution.
"""
        
        else:  # REFLECTION
            return base_prompt + """
REFLECTION PASS - Final Review

Final verification:
1. Is the solution complete?
2. Are all tests passing?
3. Any remaining issues?
4. Summary of what was done?

Provide final status and summary.
"""
    
    def _execute_pass(self, prompt: str, context: Dict) -> str:
        """Execute a single thinking pass."""
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        try:
            result = self.router.complete(messages, temperature=0.1)
            if "error" in result:
                return f"Error: {result['error']}"
            return result.get("content", "")
        except Exception as e:
            return f"Execution error: {str(e)}"
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for thinking WITH skill awareness."""
        return """You are Neuro, an expert software engineering AI with access to 259+ skills.

SKILL SYSTEM:
- You have access to specialized skills for different tasks
- Available skill categories:
  * Code Quality: code-review, code-simplifier, add-javadoc, security
  * Version Control: github, gitlab, bitbucket, iterate
  * DevOps: docker, kubernetes, vercel, azure-devops
  * Data/ML: jupyter, spark-version-upgrade, datadog
  * Frontend: frontend-design, theme-factory
  * Communication: slack, discord, notion, linear
  * Agent Memory: Learn from past experiences

THINKING PROCESS:
1. Analyze the problem thoroughly
2. Plan your approach (consider using relevant skills)
3. Implement carefully (invoke skills as needed)
4. Verify your work
5. Learn from mistakes

When working:
- Consider which skills could help at each stage
- Use code-review for quality checks
- Use security skill for auth/vulnerability tasks
- Use github skill for version control tasks
- Use docker/kubernetes for deployment tasks

Be precise, thorough, and honest about uncertainties."""
    
    def _score_convergence(self, new_response: str, best_response: str) -> float:
        """
        Score how close we are to convergence.
        Simple heuristic based on response patterns.
        """
        if not best_response:
            return 0.5
        
        # Count solution indicators
        positive = ["fix", "solution", "implemented", "complete", "verified", "pass", "success"]
        negative = ["error", "fail", "issue", "problem", "not sure", "cannot"]
        
        new_lower = new_response.lower()
        best_lower = best_response.lower()
        
        new_pos = sum(1 for w in positive if w in new_lower)
        new_neg = sum(1 for w in negative if w in new_lower)
        best_pos = sum(1 for w in positive if w in best_lower)
        best_neg = sum(1 for w in negative if w in best_lower)
        
        # Score based on positive/negative ratio
        if new_pos + new_neg == 0:
            return 0.5
        
        new_score = new_pos / (new_pos + new_neg)
        best_score = best_pos / (best_pos + best_neg) if best_pos + best_neg > 0 else 0.5
        
        # Convergence means similar high score
        return (new_score + best_score) / 2
    
    def _is_stuck(self) -> bool:
        """Detect if we're stuck in a loop."""
        if len(self.passes) < 3:
            return False
        
        # Check if last 3 passes have similar low convergence scores
        recent_scores = [p.metadata.get("score", 0) for p in self.passes[-3:]]
        if all(s < 0.6 for s in recent_scores):
            return True
        
        # Check if responses are very similar (no progress)
        recent_responses = [p.response[:200] for p in self.passes[-3:]]
        if len(set(recent_responses)) == 1:  # All identical
            return True
        
        return False
    
    def _recover_from_stuck(self, goal: str, context: Dict) -> str:
        """Recover from being stuck."""
        recovery_prompt = f"""I'm stuck on this task: {goal}

Previous attempts haven't converged. Try a different approach:

1. Re-read the original problem
2. Consider if there's a simpler solution
3. Try breaking down the problem differently
4. Look at the error messages more carefully

Provide a fresh perspective and new solution.
"""
        
        messages = [{"role": "user", "content": recovery_prompt}]
        
        try:
            result = self.router.complete(messages, temperature=0.3)
            return result.get("content", "Could not recover")
        except:
            return "Recovery failed"
    
    def _pass_to_dict(self, p: ThinkingPass) -> Dict:
        """Convert ThinkingPass to dict."""
        return {
            "type": p.pass_type.value,
            "duration_ms": p.duration_ms,
            "success": p.success,
            "response_preview": p.response[:500] if p.response else "",
            "metadata": p.metadata,
        }
    
    def get_summary(self) -> str:
        """Get a summary of the thinking loop."""
        if not self.passes:
            return "No passes completed"
        
        summary = f"Thinking Loop Summary:\n"
        summary += f"- Total passes: {len(self.passes)}\n"
        summary += f"- Convergence score: {self.convergence_score:.2f}\n"
        summary += f"- Total duration: {sum(p.duration_ms for p in self.passes)/1000:.1f}s\n"
        
        for i, p in enumerate(self.passes, 1):
            status = "✓" if p.success else "✗"
            summary += f"  Pass {i} ({p.pass_type.value}): {status} - {p.duration_ms/1000:.1f}s\n"
        
        return summary


def run_thinking_loop(
    router,
    goal: str,
    context: Optional[Dict[str, Any]] = None,
    max_passes: int = 4,
) -> Dict[str, Any]:
    """
    Convenience function to run a thinking loop.
    
    Usage:
        from neuro.reasoning.thinking_loop import run_thinking_loop
        from neuro.router import smart_router
        
        result = run_thinking_loop(
            router=smart_router,
            goal="Fix the login bug",
            max_passes=4
        )
        
        print(result["solution"])
    """
    config = LoopConfig(max_passes=max_passes)
    loop = ThinkingLoop(router, config)
    return loop.run(goal, context)
