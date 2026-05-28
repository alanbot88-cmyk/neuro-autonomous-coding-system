"""
System Prompt Scaffolding Skill
AI system prompts, LLM instructions, agent frameworks
"""

from typing import Dict, List, Any, Optional


class SystemPromptScaffoldSkill:
    """System prompt scaffolding for LLM/AI agent development"""
    
    NAME = "system_prompt"
    DESCRIPTION = "System prompt scaffolding - AI prompts, LLM instructions, agent frameworks, chain of thought"
    TRIGGERS = [
        "system prompt", "prompt engineering", "llm", "ai agent",
        "chain of thought", "few shot", "zero shot", "cot",
        "prompt template", "instruction"
    ]
    
    @classmethod
    def get_prompt_templates(cls) -> Dict[str, str]:
        return {
            "agent": '''
// AI Agent System Prompt Template
const agentPrompt = `
You are AGENT_NAME, AGENT_DESCRIPTION.

## Core Capabilities
CAPABILITIES

## Operating Principles
1. Always reason step-by-step before responding
2. Ask clarifying questions when ambiguous
3. Provide specific, actionable responses
4. Admit limitations when uncertain

## Communication Style
- Be concise but thorough
- Use code blocks for technical content
- Format output appropriately

## Constraints
CONSTRAINTS

## Context
CONTEXT

Current task: TASK
TASK_SPECIFIC_INSTRUCTIONS
`
''',

            "cot": '''
// Chain of Thought Prompt Template
const cotPrompt = `
Task: TASK

Think through this step by step:

Step 1 - Understand
What is being asked? What are the constraints?

Step 2 - Plan
How will I approach this? What steps are needed?

Step 3 - Execute
Implement the solution step by step.

Step 4 - Verify
Does this solve the task? Any edge cases?

Final Answer: Your concise response
`
''',

            "few_shot": '''
// Few-Shot Learning Prompt Template
const fewShotPrompt = `
Task: TASK

Examples:
Input: example1
Output: output1

Input: example2
Output: output2

Now solve:
Input: NEW_INPUT
Output:
'''
        }
    
    @classmethod
    def invoke(cls, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        task_lower = task.lower()
        
        result_type = "agent"
        if "chain" in task_lower or "cot" in task_lower or "thought" in task_lower:
            result_type = "cot"
        elif "few" in task_lower or "shot" in task_lower:
            result_type = "few_shot"
        
        return {
            "skill": cls.NAME,
            "result_type": result_type,
            "templates": cls.get_prompt_templates(),
            "best_practices": [
                "Be specific and explicit",
                "Include examples for complex tasks",
                "Define output format",
                "Add constraints and rules",
                "Include edge case handling"
            ]
        }


def generate_prompt(task: str, **kwargs) -> Dict[str, Any]:
    return SystemPromptScaffoldSkill.invoke(task, kwargs)
