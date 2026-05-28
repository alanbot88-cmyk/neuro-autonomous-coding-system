"""
Neuro Skill Manager - Automatic skill utilization system
Auto-loads and auto-triggers skills based on task context
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field

# Import all skill modules
from neuro.skills.automation import SkillAutomation, SkillTrigger, SkillTriggerType
from neuro.skills.mcp_integration import MCPSkill, MCPConfig, mcp_invoke
from neuro.skills.open_design_skills import OpenDesignSkills, OpenSkill, SkillCategory
from neuro.skills.agent_memory import SwarmVault, AgentMemorySkill, MemoryType, remember, recall, get_context
from neuro.skills.browser_automation import BrowserAutomation, BrowserConfig, BrowserTask, BrowserType
from neuro.skills.skill_middleware import SkillMiddleware, get_middleware, set_active_skills, apply_skill_context
from neuro.skills.skill_orchestrator import SkillOrchestrator

# NEW: ECC-inspired skills
from neuro.skills.verification_loop import VerificationLoop, VerificationCheckpoint, run_verification
from neuro.skills.python_patterns import PythonPatternsSkill, PythonPattern
from neuro.skills.continuous_learning import ContinuousLearning, InstinctStore, get_learning_system
from neuro.skills.agent_shield import AgentShieldSkill, SecurityFinding, run_security_scan
from neuro.skills.multi_agent import MultiAgentOrchestrator, SubTask, quick_orchestrate
from neuro.skills.task_decomposer import TaskDecomposer, ImplementationPlan, create_plan
from neuro.skills.autonomous_loop import AutonomousLoop, PRLoop, LoopType, run_autonomous_loop

# NEW: Shell Executor & Self-Healing skills
from neuro.skills.shell_executor import ShellExecutor, ExecutionResult, ShellError, quick_execute
from neuro.skills.playwright_tester import PlaywrightTester, AppTestReport, test_created_app
from neuro.skills.auto_fix_loop import AutoFixLoop, AutoFixConfig, AutoFixResult, quick_fix
from neuro.skills.app_launcher import AppLauncher, LaunchResult, launch_app, stop_app

# NEW: SWE-bench Competition skills
from neuro.skills.swe_bench_runner import SWEBenchRunner, BenchmarkResult, BenchmarkReport, quick_benchmark
from neuro.skills.agent_swarm import AgentSwarmCoordinator, AgentTask, AgentRole, run_swarm
from neuro.skills.swe_bench_prompts import SWEBenchPrompts, SWE_BENCH_SYSTEM_PROMPT, get_prompt_for_role

# Lazy imports for heavy skills
_lazy_imports = {
    "react_three_fiber": "neuro.skills.react_three_fiber.ReactThreeFiberSkill",
    "threejs_core": "neuro.skills.threejs_webgl.ThreeJSCoreSkill",
    "threejs": "neuro.skills.threejs_webgl.ThreeJSCoreSkill",
    "webgl": "neuro.skills.threejs_webgl.ThreeJSCoreSkill",
    "spline_design": "neuro.skills.spline_design.SplineDesignSkill",
    "glsl_shaders": "neuro.skills.glsl_shaders.GLSLShaderSkill",
    "shader": "neuro.skills.glsl_shaders.GLSLShaderSkill",
    "draco_performance": "neuro.skills.draco_performance.DracoPerformanceSkill",
    "draco": "neuro.skills.draco_performance.DracoPerformanceSkill",
    "gsap_scroll": "neuro.skills.gsap_scroll.GSAPScrollSkill",
    "gsap": "neuro.skills.gsap_scroll.GSAPScrollSkill",
    "scrolltrigger": "neuro.skills.gsap_scroll.GSAPScrollSkill",
    "framer_motion": "neuro.skills.framer_motion.FramerMotionSkill",
    "framer": "neuro.skills.framer_motion.FramerMotionSkill",
    "lenis_scroll": "neuro.skills.lenis_scroll.LenisSmoothScrollSkill",
    "lenis": "neuro.skills.lenis_scroll.LenisSmoothScrollSkill",
    "smooth_scroll": "neuro.skills.lenis_scroll.LenisSmoothScrollSkill",
    "vector_math": "neuro.skills.vector_math.VectorMathSkill",
    "matrix": "neuro.skills.vector_math.VectorMathSkill",
    "mathematics": "neuro.skills.vector_math.VectorMathSkill",
    "component_driven": "neuro.skills.component_driven.ComponentDrivenSkill",
    "system_prompt": "neuro.skills.system_prompt.SystemPromptScaffoldSkill",
    "asset_mapping": "neuro.skills.asset_mapping.AssetMappingSkill",
}

def _lazy_get_skill(name: str):
    """Lazily import and return a skill class."""
    import importlib
    if name in _lazy_imports:
        module_path = _lazy_imports[name]
        module_name, class_name = module_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    return None

@dataclass
class Skill:
    name: str
    description: str
    triggers: List[str]
    content: str
    path: Path
    
@dataclass
class SkillInvocation:
    skill_name: str
    trigger_used: str
    context: Dict[str, Any]
    result: Optional[str] = None

# Skill registry for quick lookup
SKILL_REGISTRY: Dict[str, Any] = {
    # Core skills
    "automation": SkillAutomation,
    "mcp": MCPSkill,
    "mcp_integration": MCPSkill,
    "open_design_skills": OpenDesignSkills,
    "open_skills": OpenDesignSkills,
    "agent_memory": AgentMemorySkill,
    "swarmvault": SwarmVault,
    "memory": AgentMemorySkill,
    "browser": BrowserAutomation,
    "browser_automation": BrowserAutomation,
    "playwright": BrowserAutomation,
    
    # NEW: ECC-inspired skills
    "verification_loop": VerificationLoop,
    "verification": VerificationLoop,
    "eval": VerificationLoop,
    "python_patterns": PythonPatternsSkill,
    "patterns": PythonPatternsSkill,
    "continuous_learning": ContinuousLearning,
    "instincts": ContinuousLearning,
    "learning": ContinuousLearning,
    "agent_shield": AgentShieldSkill,
    "security": AgentShieldSkill,
    "scan": AgentShieldSkill,
    "multi_agent": MultiAgentOrchestrator,
    "orchestrate": MultiAgentOrchestrator,
    "task_decomposer": TaskDecomposer,
    "plan": TaskDecomposer,
    "autonomous_loop": AutonomousLoop,
    "loop": AutonomousLoop,
    "iterate": AutonomousLoop,
    
    # NEW: Shell Executor & Self-Healing
    "shell_executor": ShellExecutor,
    "shell": ShellExecutor,
    "bash": ShellExecutor,
    "execute": ShellExecutor,
    "playwright_tester": PlaywrightTester,
    "playwright": PlaywrightTester,
    "test_app": PlaywrightTester,
    "auto_fix": AutoFixLoop,
    "fix_loop": AutoFixLoop,
    "self_heal": AutoFixLoop,
    "app_launcher": AppLauncher,
    "launch": AppLauncher,
    "start": AppLauncher,
    
    # NEW: SWE-bench Competition
    "swe_bench": SWEBenchRunner,
    "benchmark": SWEBenchRunner,
    "agent_swarm": AgentSwarmCoordinator,
    "swarm": AgentSwarmCoordinator,
    "multi_agent_coordinator": AgentSwarmCoordinator,
    "swe_prompts": SWEBenchPrompts,
    "prompts": SWEBenchPrompts,

    # 3D & Graphics Skills
    "react_three_fiber": None,  # Will be imported lazily
    "threejs_core": None,
    "threejs": None,
    "webgl": None,
    "spline_design": None,
    "glsl_shaders": None,
    "shader": None,
    "draco_performance": None,
    "draco": None,

    # Animation Skills
    "gsap_scroll": None,
    "gsap": None,
    "scrolltrigger": None,
    "framer_motion": None,
    "framer": None,
    "lenis_scroll": None,
    "lenis": None,
    "smooth_scroll": None,

    # Math & Technical Skills
    "vector_math": None,
    "matrix": None,
    "mathematics": None,

    # Development Skills
    "component_driven": None,
    "system_prompt": None,
    "asset_mapping": None,
}

class SkillManager:
    """Automatic skill loader and invoker for Neuro system"""

    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or Path(".agents/skills")
        self.skills: Dict[str, Skill] = {}
        self.invocation_log: List[SkillInvocation] = []
        
    def load_all_skills(self) -> int:
        """Load all skills from skills directory"""
        if not self.skills_dir.exists():
            return 0
            
        loaded = 0
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                skill = self._load_skill(skill_path)
                if skill:
                    self.skills[skill.name] = skill
                    loaded += 1
        return loaded
    
    def _load_skill(self, skill_path: Path) -> Optional[Skill]:
        """Load a single skill from directory"""
        try:
            content = (skill_path / "SKILL.md").read_text()
            
            # Parse YAML frontmatter
            frontmatter = {}
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    for line in parts[1].strip().split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            frontmatter[key.strip()] = value.strip().strip('"\'')
            
            name = frontmatter.get("name", skill_path.name)
            description = frontmatter.get("description", "")
            triggers_raw = frontmatter.get("triggers", "")
            triggers = [t.strip().strip("-").strip() for t in triggers_raw.split("\n") if t.strip()]
            
            return Skill(
                name=name,
                description=description,
                triggers=triggers,
                content=content,
                path=skill_path
            )
        except Exception as e:
            print(f"Error loading skill from {skill_path}: {e}")
            return None
    
    def find_matching_skills(self, task: str, context: Dict[str, Any] = None) -> List[Skill]:
        """Find skills that match the current task context"""
        matches = []
        task_lower = task.lower()
        context = context or {}
        
        for skill in self.skills.values():
            # Check triggers
            for trigger in skill.triggers:
                if trigger.lower() in task_lower:
                    matches.append(skill)
                    continue
                    
            # Check description keywords
            keywords_map = {
                "github": ["github", "pr", "pull request", "repository", "commit"],
                "gitlab": ["gitlab", "merge request"],
                "code-review": ["code review", "review", "pr review"],
                "iterate": ["iterate", "verify", "ci", "tests"],
                "security": ["security", "auth", "vulnerability"],
                "docker": ["docker", "container", "containerize"],
                "kubernetes": ["kubernetes", "k8s", "deploy"],
                "jupyter": ["jupyter", "notebook", "data science"],
                "slack-channel-monitor": ["slack", "notification", "message"],
                "discord": ["discord", "bot", "message"],
                "datadog": ["datadog", "monitoring", "metrics"],
                "linear": ["linear", "issue", "ticket"],
                "notion": ["notion", "document"],
                "frontend-design": ["frontend", "ui", "web", "design"],
                "code-simplifier": ["simplify", "refactor", "clean"],
                "security": ["security", "vulnerability", "auth"],
                "release-notes": ["changelog", "release notes"],
                # New skills
                "mcp": ["mcp", "model context", "ollama", "lm studio", "provider"],
                "open_skills": ["skills", "openhands", "plugin", "extension"],
                "agent_memory": ["memory", "remember", "learn", "context", "vault"],
                "browser": ["browser", "playwright", "web", "scrape", "navigate", "click"],
            }
            
            skill_keywords = keywords_map.get(skill.name, [])
            if any(kw in task_lower for kw in skill_keywords):
                matches.append(skill)
                
        return matches
    
    def auto_invoke(self, task: str, context: Dict[str, Any] = None) -> List[SkillInvocation]:
        """Automatically invoke relevant skills based on task"""
        matches = self.find_matching_skills(task, context)
        invocations = []
        
        for skill in matches:
            invocation = SkillInvocation(
                skill_name=skill.name,
                trigger_used=task[:100],
                context=context or {}
            )
            self.invocation_log.append(invocation)
            invocations.append(invocation)
            
        return invocations
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a specific skill by name"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """List all loaded skills"""
        return [
            {"name": s.name, "description": s.description, "triggers": s.triggers}
            for s in self.skills.values()
        ]

# Global skill manager instance
_skill_manager: Optional[SkillManager] = None

def get_skill_manager() -> SkillManager:
    """Get or create the global skill manager"""
    global _skill_manager
    if _skill_manager is None:
        _skill_manager = SkillManager()
        _skill_manager.load_all_skills()
    return _skill_manager

def auto_skills(task: str, context: Dict[str, Any] = None) -> List[SkillInvocation]:
    """Auto-detect and invoke skills for a task"""
    return get_skill_manager().auto_invoke(task, context)

def invoke_skill(skill_name: str, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Invoke a specific skill by name
    Supports all registered skills including new additions:
    - mcp, mcp_integration: Model Context Protocol integration
    - open_design_skills: OpenHands 259+ skills catalog
    - agent_memory, swarmvault: Persistent memory system
    - browser, browser_automation, playwright: Browser automation
    """
    if skill_name in SKILL_REGISTRY:
        skill_class = SKILL_REGISTRY[skill_name]
        if hasattr(skill_class, 'invoke'):
            return skill_class.invoke(task, context)
        return {"error": f"Skill {skill_name} does not have an invoke method"}
    
    # Fallback to auto-detection
    return {"auto_triggered": auto_skills(task, context)}

# Convenience functions for new skills
def mcp_connect(provider: str = "ollama", **kwargs) -> Dict[str, Any]:
    """Quick MCP connection"""
    return mcp_invoke("connect", provider=provider, **kwargs)

def browse_web(task: str, **kwargs) -> Dict[str, Any]:
    """Quick browser automation"""
    return BrowserAutomation.invoke(task, kwargs if kwargs else None)

def store_memory(content: str, **kwargs) -> Any:
    """Quick memory storage"""
    return remember(content, **kwargs)

def search_memory(query: str, **kwargs) -> List:
    """Quick memory recall"""
    return recall(query, **kwargs)
