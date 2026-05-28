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

Usage:
    from neuro import create_agent
    
    agent = create_agent(goal="Fix the bug")
    result = agent.run()
"""

__version__ = "0.1.0"
__target__ = "75-80% SWE-bench"

from neuro.executor.agent_loop import create_agent, run_goal, NeuroAgent, AgentResult, AgentConfig

__all__ = [
    "create_agent",
    "run_goal",
    "NeuroAgent",
    "AgentResult",
    "AgentConfig",
]
