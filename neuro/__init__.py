"""
Neuro Autonomous Agent - High-performance coding agent using free APIs
Target: 75-80% on SWE-bench benchmarks

Architecture:
- Smart Router: Rotates across free API providers
- Chain-of-Thought: Simulates reasoning mode
- Multi-Pass Thinking: Error correction loop
- Test-First Validation: Prevents broken patches
- Patch Guards: Only applies verified changes
- Memory System: Learns from past failures
- Skill Automation: Auto-triggers 40+ integrated skills based on task context

Usage:
    from neuro import create_agent

    agent = create_agent(goal="Fix the bug")
    result = agent.run()
    
Skill Integration:
    from neuro.skills import auto_skills
    
    # Auto-detect and invoke relevant skills
    result = auto_skills("Fix security vulnerability in authentication", {"file_path": "auth.py"})
"""

__version__ = "1.0.0"
__target__ = "75-80% SWE-bench"

from neuro.executor.agent_loop import create_agent, run_goal, NeuroAgent, AgentResult, AgentConfig
from neuro.skills import SkillAutomation, get_skill_manager, auto_skills

__all__ = [
    "create_agent",
    "run_goal",
    "NeuroAgent",
    "AgentResult",
    "AgentConfig",
    "SkillAutomation",
    "get_skill_manager",
    "auto_skills",
]
