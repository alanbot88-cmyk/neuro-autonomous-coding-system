"""
Skill Orchestrator - Coordinates 259+ skills across agent lifecycle
"""

from typing import Dict, List, Any, Optional

# Import directly from modules to avoid circular imports
from neuro.skills.automation import SkillAutomation
from neuro.skills.open_design_skills import OpenDesignSkills
from neuro.skills.agent_memory import remember, recall, get_context as get_memory_context, MemoryType

# SKILL_REGISTRY will be set after all imports complete
SKILL_REGISTRY = {}


class SkillOrchestrator:
    """
    Orchestrates all 259+ skills across the agent lifecycle.
    Skills are auto-detected and invoked at appropriate stages.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.active_skills: List[str] = []
        self.skill_results: Dict[str, Any] = {}
        # Lazy import SKILL_REGISTRY to avoid circular imports
        self._registry = None
    
    @property
    def skill_registry(self):
        """Lazy load SKILL_REGISTRY to avoid circular imports."""
        if self._registry is None:
            from neuro.skills import SKILL_REGISTRY as _reg
            self._registry = _reg
        return self._registry
    
    def detect_skills(self, goal: str, context: Dict[str, Any] = None) -> List[str]:
        """Auto-detect which skills to invoke based on goal and context."""
        context = context or {}
        
        # Use SkillAutomation for keyword-based detection
        trigger_result = SkillAutomation.auto_trigger(goal, context)
        detected = trigger_result.get("detected_skills", [])
        
        # Also check OpenDesignSkills for specific matches
        open_result = OpenDesignSkills.invoke(goal, context)
        for skill in open_result.get("matched_skills", []):
            if skill["name"] not in detected:
                detected.append(skill["name"])
        
        self.active_skills = list(set(detected))
        
        if self.verbose and self.active_skills:
            print(f"🎯 Skills detected: {', '.join(self.active_skills)}")
        
        return self.active_skills
    
    def enrich_context(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich context with skill-specific information."""
        enriched = context.copy()
        skill_hints = []
        
        for skill_name in self.active_skills:
            try:
                # Get skill-specific context
                registry = self.skill_registry
                if skill_name in registry:
                    skill_class = registry[skill_name]
                    if hasattr(skill_class, 'invoke'):
                        result = skill_class.invoke(goal, {"context": context})
                        self.skill_results[skill_name] = result
                        
                        # Add skill-specific hints to context
                        if "capabilities" in result:
                            skill_hints.append(f"[{skill_name}]: {result.get('capabilities', [])[:3]}")
                        
                        # Add MCP endpoint if available
                        if "endpoint" in result:
                            enriched[f"{skill_name}_endpoint"] = result["endpoint"]
                        
                        # Add memory context if available
                        if skill_name in ["agent_memory", "swarmvault"]:
                            mem_context = get_memory_context(goal)
                            if mem_context:
                                enriched["memory_context"] = mem_context
                        
                        # Add browser config if available
                        if skill_name in ["browser_automation", "playwright"]:
                            if "config" in result:
                                enriched["browser_config"] = result["config"]
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Skill {skill_name} error: {e}")
        
        if skill_hints:
            enriched["skill_hints"] = "\n".join(skill_hints)
        
        return enriched
    
    def invoke_skills_for_stage(self, stage: str, data: Any) -> Dict[str, Any]:
        """Invoke relevant skills for a specific execution stage."""
        results = {}
        
        # Stage-specific skill invocation
        stage_skills = {
            "analysis": ["code-review", "security", "code-simplifier"],
            "implementation": ["github", "git", "docker"],
            "testing": ["qa-changes", "iterate"],
            "deployment": ["docker", "kubernetes", "vercel"],
            "monitoring": ["datadog", "slack-channel-monitor"],
        }
        
        registry = self.skill_registry
        for skill_name in self.active_skills:
            if skill_name in stage_skills.get(stage, []):
                try:
                    if skill_name in registry:
                        skill_class = registry[skill_name]
                        if hasattr(skill_class, 'invoke'):
                            result = skill_class.invoke(str(data), {"stage": stage})
                            results[skill_name] = result
                except:
                    pass
        
        return results
    
    def learn_from_task(self, goal: str, success: bool, context: Dict[str, Any]):
        """Store learning from task completion in agent memory."""
        try:
            summary = f"Task: {goal[:100]}... Success: {success}"
            tags = self.active_skills.copy()
            if success:
                tags.append("success")
            else:
                tags.append("failure")
            
            remember(
                content=summary,
                memory_type=MemoryType.EPISODIC,
                tags=tags,
                context=context
            )
        except:
            pass
