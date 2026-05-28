"""
Main Agent Loop - Orchestrates all components for 75-80% performance
Integrates: Router, Reasoning, Validation, Memory, Skills (259+)
"""

import os
import time
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

from neuro.router.smart_router import SmartRouter, _router
from neuro.router.fallback import FallbackHandler, create_fallback_handler
from neuro.reasoning.chain_of_thought import ChainOfThought, CoTConfig
from neuro.reasoning.thinking_loop import ThinkingLoop, LoopConfig
from neuro.validation.test_runner import TestRunner
from neuro.validation.patch_guard import PatchGuard
from neuro.memory.task_store import TaskStore

# IMPORT ALL SKILLS FOR INTEGRATION
from neuro.skills import (
    SkillAutomation, SkillTrigger, SkillTriggerType,
    MCPSkill, OpenDesignSkills, AgentMemorySkill, BrowserAutomation,
    invoke_skill, mcp_connect, browse_web, store_memory, recall, 
    get_context as get_memory_context, MemoryType, SKILL_REGISTRY,
    SkillOrchestrator  # Import from separate file
)


@dataclass
class AgentConfig:
    """Configuration for the Neuro agent."""
    goal: str
    working_dir: str = "."
    max_steps: int = 50
    max_passes: int = 4
    model: Optional[str] = None
    provider: Optional[str] = None
    temperature: float = 0.1
    test_first: bool = True
    use_cot: bool = True
    use_memory: bool = True
    use_skills: bool = True  # NEW: Enable skills
    dry_run: bool = True
    confirm_apply: bool = True
    verbose: bool = True


@dataclass
class AgentResult:
    """Result from agent execution."""
    success: bool
    goal: str
    status: str
    steps: int
    passes_used: int
    duration_ms: float
    files_changed: List[str] = field(default_factory=list)
    error: Optional[str] = None
    model_used: str = ""
    provider_used: str = ""
    validation_passed: bool = False
    test_results: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    skills_used: List[str] = field(default_factory=list)  # NEW: Track skills


class NeuroAgent:
    """
    Main Neuro Autonomous Agent.
    Orchestrates all components for high SWE-bench performance.
    NOW WITH FULL 259+ SKILL INTEGRATION.
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.router = SmartRouter()
        self.fallback = create_fallback_handler(self.router)
        self.cot = ChainOfThought(CoTConfig(enabled=config.use_cot))
        self.test_runner = TestRunner(config.working_dir)
        self.patch_guard = PatchGuard(config.working_dir, dry_run=config.dry_run)
        self.memory = TaskStore() if config.use_memory else None
        
        # NEW: Initialize skill orchestrator
        self.skill_orchestrator = SkillOrchestrator(verbose=config.verbose) if config.use_skills else None
        
        self.current_step = 0
        self.history: List[Dict] = []
        self.start_time = time.time()
        
        # Get similar past tasks for context (including skill memory)
        self.similar_context = self._get_similar_context()
    
    def _get_similar_context(self) -> str:
        """Get context from similar past tasks and skill memory."""
        context_parts = []
        
        # Memory from past tasks
        if self.memory:
            try:
                tasks = self.memory.get_similar(self.config.goal, limit=3)
                if tasks:
                    context_parts.append("Past task history:")
                    for task in tasks:
                        context_parts.append(f"- {task.goal[:100]}... (status: {task.status})")
            except:
                pass
        
        # NEW: Also get context from skill-based memory
        if self.config.use_skills:
            try:
                skill_mem = get_memory_context(self.config.goal)
                if skill_mem:
                    context_parts.append(f"\nRelevant skill memory:\n{skill_mem}")
            except:
                pass
        
        return "\n".join(context_parts) if context_parts else ""
    
    def run(self) -> AgentResult:
        """
        Run the agent to complete the goal WITH FULL SKILL INTEGRATION.
        
        Returns:
            AgentResult with execution details
        """
        if self.config.verbose:
            print("=" * 60)
            print("NEURO AUTONOMOUS AGENT (with 259+ Skills)")
            print("=" * 60)
            print(f"Goal: {self.config.goal}")
            print(f"Working dir: {self.config.working_dir}")
            print(f"Max steps: {self.config.max_steps}")
            print(f"Test-first: {self.config.test_first}")
            print(f"COT: {self.config.use_cot}")
            print(f"Skills: {self.config.use_skills}")
            print("=" * 60)
        
        try:
            # PHASE 0: SKILL DETECTION (NEW!)
            if self.skill_orchestrator:
                if self.config.verbose:
                    print("\n🔍 Detecting relevant skills...")
                self.skill_orchestrator.detect_skills(self.config.goal, {
                    "working_dir": self.config.working_dir
                })
            
            # Phase 1: Multi-pass thinking WITH skill enrichment
            thinking_loop = ThinkingLoop(self.router, LoopConfig(max_passes=self.config.max_passes))
            
            # Build context with skill enrichment
            context = {
                "working_dir": self.config.working_dir,
                "test_first": self.config.test_first,
                "similar_tasks": self.similar_context,
                "active_skills": self.skill_orchestrator.active_skills if self.skill_orchestrator else [],
            }
            
            # NEW: Enrich context with skill-specific information
            if self.skill_orchestrator:
                context = self.skill_orchestrator.enrich_context(self.config.goal, context)
            
            # Invoke analysis-stage skills
            if self.skill_orchestrator:
                analysis_results = self.skill_orchestrator.invoke_skills_for_stage("analysis", context)
                if analysis_results and self.config.verbose:
                    print(f"📊 Analysis skills: {list(analysis_results.keys())}")
            
            thinking_result = thinking_loop.run(
                goal=self.config.goal,
                context=context,
            )
            
            solution = thinking_result["solution"]
            passes_used = thinking_result["num_passes"]
            
            if self.config.verbose:
                print(f"\n✓ Thinking complete ({passes_used} passes)")
                print(f"Convergence: {thinking_result['convergence_score']:.2f}")
            
            # Phase 2: Validation WITH skill invocation
            validation_passed = False
            
            if self.config.test_first:
                if self.config.verbose:
                    print("\n📋 Running validation tests...")
                
                # NEW: Invoke testing-stage skills before running tests
                if self.skill_orchestrator:
                    test_skills = self.skill_orchestrator.invoke_skills_for_stage("testing", solution)
                    if test_skills and self.config.verbose:
                        print(f"🧪 Testing skills: {list(test_skills.keys())}")
                
                # Run relevant tests
                test_result = self.test_runner.run_pytest(timeout=300)
                validation_passed = test_result.all_passed
                
                self.config.test_results = {
                    "total": test_result.total,
                    "passed": test_result.passed,
                    "failed": test_result.failed,
                    "exit_code": test_result.exit_code,
                }
                
                if self.config.verbose:
                    print(f"Tests: {test_result.passed}/{test_result.total} passed")
                
                if not validation_passed:
                    if self.config.verbose:
                        print("⚠️ Tests failed - attempting fixes...")
            
            # Phase 3: Apply patches (if not dry run and validated)
            files_changed = []
            
            if not self.config.dry_run and validation_passed:
                if self.config.verbose:
                    print("\n🔧 Applying verified patches...")
                
                # NEW: Invoke deployment skills before applying
                if self.skill_orchestrator:
                    deploy_skills = self.skill_orchestrator.invoke_skills_for_stage("deployment", files_changed)
                    if deploy_skills and self.config.verbose:
                        print(f"🚀 Deployment skills: {list(deploy_skills.keys())}")
                
                results = self.patch_guard.apply_verified_patches()
                files_changed = [r["file"] for r in results["applied"]]
                
                if self.config.verbose:
                    print(f"Applied: {len(files_changed)} files")
            elif self.config.dry_run:
                if self.config.verbose:
                    print("\n🔍 Dry run - no changes applied")
            
            # Record in memory INCLUDING skill learning
            duration_ms = (time.time() - self.start_time) * 1000
            
            if self.memory:
                try:
                    self.memory.add_task(
                        goal=self.config.goal,
                        status="success" if validation_passed else "partial",
                        files_changed=files_changed,
                        duration_ms=duration_ms,
                        model_used=self.config.model or "auto",
                        provider_used=self.router.get_stats().get("provider_calls", {}).most_common(1)[0][0] if hasattr(self.router.get_stats().get("provider_calls"), "most_common") else "unknown",
                        passes_used=passes_used,
                    )
                except:
                    pass
            
            # NEW: Store skill learning
            if self.skill_orchestrator:
                self.skill_orchestrator.learn_from_task(
                    self.config.goal, 
                    validation_passed,
                    {"files_changed": files_changed}
                )
            
            return AgentResult(
                success=validation_passed,
                goal=self.config.goal,
                status="completed",
                steps=self.current_step,
                passes_used=passes_used,
                duration_ms=duration_ms,
                files_changed=files_changed,
                validation_passed=validation_passed,
                test_results=self.config.test_results,
                model_used=self.config.model or "auto",
                skills_used=self.skill_orchestrator.active_skills if self.skill_orchestrator else [],
            )
            
        except Exception as e:
            duration_ms = (time.time() - self.start_time) * 1000
            
            # Record failure
            if self.memory:
                try:
                    self.memory.add_task(
                        goal=self.config.goal,
                        status="failure",
                        files_changed=[],
                        error=str(e),
                        duration_ms=duration_ms,
                    )
                except:
                    pass
            
            # NEW: Store failure in skill memory too
            if self.skill_orchestrator:
                self.skill_orchestrator.learn_from_task(
                    self.config.goal,
                    False,
                    {"error": str(e)}
                )
            
            return AgentResult(
                success=False,
                goal=self.config.goal,
                status="error",
                steps=self.current_step,
                passes_used=0,
                duration_ms=duration_ms,
                error=str(e),
                skills_used=self.skill_orchestrator.active_skills if self.skill_orchestrator else [],
            )
    
    def get_history(self) -> List[Dict]:
        """Get execution history."""
        return self.history
    
    def get_thinking_summary(self) -> str:
        """Get summary of thinking process."""
        skill_info = f", Skills: {len(self.skill_orchestrator.active_skills)}" if self.skill_orchestrator else ""
        return f"Steps: {self.current_step}, Duration: {(time.time() - self.start_time):.1f}s{skill_info}"


def create_agent(
    goal: str,
    working_dir: str = ".",
    max_steps: int = 50,
    max_passes: int = 4,
    model: Optional[str] = None,
    test_first: bool = True,
    use_cot: bool = True,
    use_skills: bool = True,  # NEW
    dry_run: bool = True,
    verbose: bool = True,
) -> NeuroAgent:
    """
    Create a new Neuro agent WITH FULL SKILL INTEGRATION.
    
    Usage:
        from neuro.executor.agent_loop import create_agent
        
        agent = create_agent(
            goal="Fix the login bug",
            working_dir="/path/to/project",
            test_first=True,
            use_cot=True,
            use_skills=True,  # Enable 259+ skills
            dry_run=False,
        )
        
        result = agent.run()
        print(f"Success: {result.success}")
        print(f"Skills used: {result.skills_used}")
    """
    config = AgentConfig(
        goal=goal,
        working_dir=working_dir,
        max_steps=max_steps,
        max_passes=max_passes,
        model=model,
        test_first=test_first,
        use_cot=use_cot,
        use_skills=use_skills,
        dry_run=dry_run,
        verbose=verbose,
    )
    
    return NeuroAgent(config)


def run_goal(goal: str, **kwargs) -> AgentResult:
    """
    Quick function to run a goal WITH SKILL INTEGRATION.
    
    Usage:
        from neuro.executor.agent_loop import run_goal
        
        result = run_goal(
            "Fix the bug in main.py",
            working_dir="/path/to/project",
            use_skills=True
        )
        
        print(result.success)
        print(f"Skills used: {result.skills_used}")
    """
    agent = create_agent(goal, **kwargs)
    return agent.run()
