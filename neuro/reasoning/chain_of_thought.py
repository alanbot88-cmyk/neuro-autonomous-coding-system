"""
Chain of Thought Prompting - Simulates reasoning mode
Key component for achieving 75-80% on SWE-bench
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class CoTConfig:
    """Configuration for chain-of-thought."""
    enabled: bool = True
    thinking_steps: int = 5
    include_reasoning_markers: bool = True
    force_reflection: bool = True
    strategy: str = "zero_shot_cot"  # zero_shot_cot, few_shot_cot, auto_cot


# COT Prompt Templates
COT_PROMPTS = {
    "zero_shot_cot": """Let me think through this step by step:

1. First, I need to understand the problem...
2. Then, I should identify what changes are needed...
3. Next, I'll implement the fix...
4. After that, I need to verify it works...
5. Finally, I'll ensure no regressions...

Let me start by analyzing the issue: {goal}

Working through this:

Step 1 - Understanding:
{analysis_step1}

Step 2 - Planning:
{analysis_step2}

Step 3 - Implementation:
{analysis_step3}

Step 4 - Verification:
{analysis_step4}

Step 5 - Final check:
{analysis_step5}

Based on this reasoning, my approach is:
{conclusion}""",

    "analyze_before_code": """Before writing any code, I must understand:

1. The Issue
   - What is the expected behavior?
   - What is the actual behavior?
   - What error messages exist?

2. The Context
   - Which file(s) are affected?
   - What functions/modules are involved?
   - Are there related tests?

3. The Solution Path
   - What changes are needed?
   - Are there similar patterns in the codebase?
   - What edge cases must be handled?

4. Verification
   - How will I test this fix?
   - What should I NOT change?
   - What could break?

Let me analyze: {goal}

ISSUE ANALYSIS:
{issue}

CONTEXT DISCOVERY:
{context}

SOLUTION PLAN:
{plan}

VERIFICATION STRATEGY:
{verification}

IMPLEMENTATION:
{implementation}""",

    "test_driven": """Following test-driven approach:

1. READ TEST FIRST - Understand expected behavior
2. WRITE CODE TO PASS TEST - Implement fix
3. VERIFY TEST PASSES - Confirm fix works
4. CHECK NO REGRESSIONS - Ensure nothing else broke

GOAL: {goal}

TEST ANALYSIS (Step 1):
Running relevant tests to understand expected behavior...
{test_analysis}

CODE IMPLEMENTATION (Step 2):
Writing code that passes the test...
{implementation}

VERIFICATION (Step 3):
Test result: {test_result}

REGRESSION CHECK (Step 4):
Checking other tests and functionality...
{regression_check}

FINAL VERDICT: {verdict}""",

    "debug_reflect": """When debugging, I must:

1. READ THE ERROR carefully
2. FIND THE ROOT CAUSE (not symptoms)
3. PLAN THE FIX (not trial-and-error)
4. IMPLEMENT CAREFULLY
5. VERIFY THE FIX
6. REFLECT ON LESSONS

ERROR: {error}

ROOT CAUSE ANALYSIS:
{root_cause}

FIX PLAN:
{fix_plan}

IMPLEMENTATION:
{implementation}

VERIFICATION:
{verification}

LESSONS LEARNED:
{lessons}""",
}


class ChainOfThought:
    """
    Chain-of-Thought prompting to simulate reasoning mode.
    Critical for achieving high SWE-bench scores with free models.
    """
    
    def __init__(self, config: Optional[CoTConfig] = None):
        self.config = config or CoTConfig()
        self.thinking_history: List[Dict] = []
    
    def wrap_with_cot(self, goal: str, context: Optional[str] = None) -> str:
        """
        Wrap a goal with chain-of-thought prompting.
        
        Args:
            goal: The original task goal
            context: Optional context (code, errors, etc.)
            
        Returns:
            Goal wrapped with CoT prompting
        """
        if not self.config.enabled:
            return goal
        
        template = COT_PROMPTS.get(self.config.strategy, COT_PROMPTS["zero_shot_cot"])
        
        # Fill in the placeholders
        wrapped = template.format(
            goal=goal,
            analysis_step1=self._analyze_step1(goal, context),
            analysis_step2=self._analyze_step2(goal, context),
            analysis_step3=self._analyze_step3(goal, context),
            analysis_step4=self._analyze_step4(goal, context),
            analysis_step5=self._analyze_step5(goal, context),
            conclusion=self._conclude(goal),
            issue=self._get_issue(goal),
            context=self._get_context(context) if context else "Will discover through code analysis",
            plan=self._get_plan(goal),
            verification=self._get_verification(goal),
            implementation=self._get_implementation(),
            test_analysis=self._get_test_analysis(),
            test_result=self._get_test_result(),
            regression_check=self._get_regression_check(),
            verdict="PENDING - need to run tests",
            error=self._get_error(goal),
            root_cause=self._get_root_cause(),
            fix_plan=self._get_fix_plan(),
            lessons=self._get_lessons(),
        )
        
        return wrapped
    
    def wrap_system_prompt(self, base_system: str) -> str:
        """Enhance system prompt with CoT instructions."""
        if not self.config.enabled:
            return base_system
        
        cot_instruction = """

CHAIN-OF-THOUGHT INSTRUCTIONS:
- Think step by step before executing
- Analyze the problem deeply before coding
- Plan your approach before implementation
- Verify your solution before claiming success
- Reflect on what you learned after each step
- When debugging: find root cause, not symptoms

Always follow this pattern:
1. UNDERSTAND - What is the issue?
2. PLAN - What changes are needed?
3. EXECUTE - Make the changes
4. VERIFY - Run tests to confirm
5. REFLECT - What did we learn?

Do NOT:
- Guess and check randomly
- Apply patches without testing
- Claim success without verification
- Ignore error messages"""
        
        return base_system + cot_instruction
    
    def create_thinking_prompt(self, goal: str, step_number: int, total_steps: int) -> str:
        """
        Create a single thinking step prompt.
        
        Args:
            goal: The task goal
            step_number: Current step (1-indexed)
            total_steps: Total number of thinking steps
            
        Returns:
            Thinking prompt for this step
        """
        templates = [
            # Step 1: Understanding
            f"""THINKING STEP {step_number}/{total_steps}: UNDERSTAND THE PROBLEM

Task: {goal}

Before proceeding, I must understand:
1. What is the expected behavior?
2. What is the actual behavior?
3. What error messages or symptoms exist?
4. Which parts of the codebase are relevant?

Let me analyze the problem in detail:
""",
            
            # Step 2: Planning
            f"""THINKING STEP {step_number}/{total_steps}: PLAN THE APPROACH

Based on my understanding, here's my plan:
1. First, I will [action]
2. Then, I will [action]
3. Finally, I will [action]

Potential challenges and how I'll address them:
- Challenge 1: [mitigation]
- Challenge 2: [mitigation]

My confidence level: [high/medium/low] because [reasoning]

Let me proceed with this plan:
""",
            
            # Step 3: Execution
            f"""THINKING STEP {step_number}/{total_steps}: EXECUTE THE PLAN

Executing: [specific actions based on plan]

Current status:
- Step 3a: [action] - [result]
- Step 3b: [action] - [result]
- Step 3c: [action] - [result]

Any adjustments needed based on results?
[yes/no] - [reasoning]

Proceeding with next steps:
""",
            
            # Step 4: Verification
            f"""THINKING STEP {step_number}/{total_steps}: VERIFY THE SOLUTION

I need to verify that my changes are correct:

1. Run tests: [test command] - does it pass?
2. Check no regressions: [other tests] - do they pass?
3. Manual verification: [what to check manually]

If tests fail:
- Error: [error message]
- Root cause: [analysis]
- Fix: [adjusted approach]

If all tests pass:
- Solution is verified
- Can proceed to claim success

Let me run verification:
""",
            
            # Step 5: Reflection
            f"""THINKING STEP {step_number}/{total_steps}: REFLECT AND SUMMARIZE

After completing this task:

What I did:
1. [summary of actions]

What worked:
1. [successful approaches]

What was challenging:
1. [difficult parts]

What I learned:
1. [insights for future tasks]

Is there anything to improve for similar tasks?
[yes/no] - [improvements]

Final status: [success/failure] because [reasoning]
""",
        ]
        
        return templates[min(step_number - 1, len(templates) - 1)]
    
    def inject_self_reflection(self, previous_output: str, goal: str) -> str:
        """
        Inject self-reflection after a response.
        
        Args:
            previous_output: The previous model response
            goal: The original goal
            
        Returns:
            Prompt encouraging self-reflection
        """
        return f"""Review your previous response:

{previous_output[:2000]}

For the task: {goal}

Self-reflection checklist:
1. Did I understand the problem correctly? [yes/no/partially] - [reasoning]
2. Is my solution complete? [yes/no/partially] - [reasoning]
3. Did I verify my solution? [yes/no/how] - [reasoning]
4. Are there potential issues I missed? [list issues]
5. What could I improve? [suggestions]

If you identify issues, please revise your response accordingly.
"""
    
    # Helper methods for template filling
    def _analyze_step1(self, goal: str, context: Optional[str]) -> str:
        return f"Analyzing: {goal[:100]}..."
    
    def _analyze_step2(self, goal: str, context: Optional[str]) -> str:
        return "Discovering relevant code context..."
    
    def _analyze_step3(self, goal: str, context: Optional[str]) -> str:
        return "Implementing necessary changes..."
    
    def _analyze_step4(self, goal: str, context: Optional[str]) -> str:
        return "Running tests to verify..."
    
    def _analyze_step5(self, goal: str, context: Optional[str]) -> str:
        return "Checking for regressions..."
    
    def _conclude(self, goal: str) -> str:
        return f"Based on step-by-step analysis of: {goal}"
    
    def _get_issue(self, goal: str) -> str:
        return "Will analyze from test output and error messages"
    
    def _get_context(self, context: str) -> str:
        return context[:500] if context else ""
    
    def _get_plan(self, goal: str) -> str:
        return "Will develop plan based on issue analysis"
    
    def _get_verification(self, goal: str) -> str:
        return "Run relevant tests to confirm fix"
    
    def _get_implementation(self) -> str:
        return "Code changes will be made here"
    
    def _get_test_analysis(self) -> str:
        return "Analyzing test expectations..."
    
    def _get_test_result(self) -> str:
        return "Need to run tests to determine"
    
    def _get_regression_check(self) -> str:
        return "Running full test suite..."
    
    def _get_error(self, goal: str) -> str:
        return "Will extract from execution output"
    
    def _get_root_cause(self) -> str:
        return "Analyzing error trace and code..."
    
    def _get_fix_plan(self) -> str:
        return "Developing fix based on root cause..."
    
    def _get_lessons(self) -> str:
        return "Summarizing lessons learned..."


# Convenience function
def create_cot_prompt(goal: str, context: Optional[str] = None, 
                      strategy: str = "zero_shot_cot") -> str:
    """
    Create a chain-of-thought prompt.
    
    Usage:
        from neuro.reasoning.chain_of_thought import create_cot_prompt
        
        prompt = create_cot_prompt(
            goal="Fix the bug in login.py",
            context="Error: NoneType has no attribute 'get'"
        )
    """
    config = CoTConfig(strategy=strategy)
    cot = ChainOfThought(config)
    return cot.wrap_with_cot(goal, context)


def wrap_system_for_cot(base_system: str) -> str:
    """
    Wrap a system prompt with CoT instructions.
    
    Usage:
        system = wrap_system_for_cot(base_system)
    """
    cot = ChainOfThought()
    return cot.wrap_system_prompt(base_system)
