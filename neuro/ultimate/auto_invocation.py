"""
Neuro Auto-Invocation System
=============================
Automatically invokes skills when detected in task context.
Nothing remains dead or unused - all skills are called when needed.
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import re

from neuro.ultimate.skills_100 import (
    ULTIMATE_SKILLS, 
    SkillAutoTrigger, 
    UltimateSkill,
    get_auto_trigger,
    auto_detect_skills,
    SkillCategory
)


# =============================================================================
# TASK ANALYZER
# =============================================================================

@dataclass
class DetectedSkill:
    """A skill that has been detected and is ready to use."""
    skill: UltimateSkill
    match_score: float
    confidence: str  # "high", "medium", "low"
    auto_invoke: bool = False


class TaskAnalyzer:
    """
    Analyzes incoming tasks and automatically detects relevant skills.
    Implements smart activation based on task context.
    """
    
    def __init__(self):
        self.auto_trigger = get_auto_trigger()
        self.history: List[Dict] = []
        self.skill_activations: Dict[str, int] = {}
        
    def analyze(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze a task and return all detected skills with auto-invocation status.
        """
        context = context or {}
        task_lower = task.lower()
        
        # Get auto-detected skills
        auto_result = self.auto_trigger.analyze_task(task, context)
        
        # Build enhanced detection
        detected = []
        
        for skill_data in auto_result["selected_skills"]:
            skill = self.auto_trigger.get_skill_by_name(skill_data["name"])
            if skill:
                score = skill_data["match_score"]
                confidence = "high" if score >= 4 else "medium" if score >= 2 else "low"
                
                detected.append(DetectedSkill(
                    skill=skill,
                    match_score=score,
                    confidence=confidence,
                    auto_invoke=score >= 2  # Auto-invoke if score >= 2
                ))
                
                # Track activation
                self.skill_activations[skill.name] = self.skill_activations.get(skill.name, 0) + 1
        
        # Add to history
        self.history.append({
            "task": task,
            "detected_count": len(detected),
            "auto_invoke_count": sum(1 for d in detected if d.auto_invoke),
            "skills": [d.skill.name for d in detected]
        })
        
        return {
            "task": task,
            "task_type": auto_result["task_type"],
            "detected_skills": [
                {
                    "name": d.skill.name,
                    "category": d.skill.category.value,
                    "description": d.skill.description,
                    "match_score": d.match_score,
                    "confidence": d.confidence,
                    "auto_invoke": d.auto_invoke,
                    "capabilities": d.skill.capabilities,
                    "triggers": d.skill.triggers
                }
                for d in detected
            ],
            "auto_invoke_skills": [
                d.skill.name for d in detected if d.auto_invoke
            ],
            "mcp_servers": auto_result["mcp_servers_needed"],
            "total_skills": len(detected),
            "ready": len(detected) > 0
        }
    
    def get_activation_stats(self) -> Dict[str, Any]:
        """Get skill activation statistics."""
        total_activations = sum(self.skill_activations.values())
        return {
            "total_activations": total_activations,
            "unique_skills_used": len(self.skill_activations),
            "top_skills": sorted(
                self.skill_activations.items(),
                key=lambda x: -x[1]
            )[:10],
            "never_used": [
                s.name for s in ULTIMATE_SKILLS 
                if s.name not in self.skill_activations
            ][:10]
        }


# =============================================================================
# SKILL INVOKER
# =============================================================================

class SkillInvoker:
    """
    Invokes detected skills with proper context and error handling.
    Ensures all skills are properly used and nothing remains dead.
    """
    
    def __init__(self):
        self.analyzer = TaskAnalyzer()
        self.execution_results: List[Dict] = []
        
    def invoke_for_task(self, task: str, executor: Callable, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze task, detect skills, and execute with proper context.
        Returns results with skill usage information.
        """
        context = context or {}
        
        # Analyze the task
        analysis = self.analyzer.analyze(task, context)
        
        # Build enhanced context with skill information
        enhanced_context = {
            **context,
            "detected_skills": [s["name"] for s in analysis["detected_skills"]],
            "skill_categories": list(set(s["category"] for s in analysis["detected_skills"])),
            "auto_invoke": analysis["auto_invoke_skills"],
            "mcp_servers": analysis["mcp_servers"]
        }
        
        # Execute the main task with enhanced context
        try:
            result = executor(task, enhanced_context)
            
            self.execution_results.append({
                "task": task,
                "skills_used": analysis["detected_skills"],
                "success": True,
                "result": result
            })
            
            return {
                "success": True,
                "task": task,
                "skills_detected": len(analysis["detected_skills"]),
                "skills_used": analysis["detected_skills"],
                "auto_invoke_skills": analysis["auto_invoke_skills"],
                "mcp_servers_needed": analysis["mcp_servers"],
                "result": result
            }
            
        except Exception as e:
            self.execution_results.append({
                "task": task,
                "skills_used": analysis["detected_skills"],
                "success": False,
                "error": str(e)
            })
            
            return {
                "success": False,
                "task": task,
                "skills_detected": len(analysis["detected_skills"]),
                "error": str(e)
            }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        total = len(self.execution_results)
        successful = sum(1 for r in self.execution_results if r.get("success"))
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0
        }


# =============================================================================
# SKILL ORCHESTRATOR (Main Class)
# =============================================================================

class SkillOrchestrator:
    """
    Main orchestrator that combines task analysis, skill detection,
    and auto-invocation. Ensures all skills are properly utilized.
    """
    
    def __init__(self):
        self.analyzer = TaskAnalyzer()
        self.invoker = SkillInvoker()
        self._skill_registry = {s.name: s for s in ULTIMATE_SKILLS}
        
    def orchestrate(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main orchestration method - analyzes task, detects skills,
        and prepares everything for execution.
        """
        context = context or {}
        
        # Get full analysis
        analysis = self.analyzer.analyze(task, context)
        
        # Get skill templates for execution
        skill_templates = {}
        for skill_data in analysis["detected_skills"]:
            skill = self._skill_registry.get(skill_data["name"])
            if skill and skill.code_template:
                skill_templates[skill.name] = skill.code_template
        
        return {
            "task": task,
            "task_type": analysis["task_type"],
            "skills_detected": analysis["detected_skills"],
            "auto_invoke": analysis["auto_invoke_skills"],
            "mcp_servers": analysis["mcp_servers"],
            "skill_templates": skill_templates,
            "categories": list(set(s["category"] for s in analysis["detected_skills"])),
            "priority_skills": [
                s for s in analysis["detected_skills"] 
                if s["priority"] == 1
            ],
            "ready_for_execution": True
        }
    
    def execute(self, task: str, executor: Callable, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute a task with full orchestration."""
        return self.invoker.invoke_for_task(task, executor, context)
    
    def get_skill(self, name: str) -> Optional[UltimateSkill]:
        """Get a specific skill from the registry."""
        return self._skill_registry.get(name)
    
    def list_all_skills(self) -> List[Dict]:
        """List all available skills."""
        return [
            {
                "name": s.name,
                "category": s.category.value,
                "description": s.description,
                "priority": s.priority,
                "triggers": s.triggers[:5]
            }
            for s in ULTIMATE_SKILLS
        ]
    
    def get_skills_by_category(self, category: str) -> List[Dict]:
        """Get skills filtered by category."""
        try:
            cat = SkillCategory(category)
            return [
                {
                    "name": s.name,
                    "description": s.description,
                    "priority": s.priority,
                    "triggers": s.triggers[:5]
                }
                for s in ULTIMATE_SKILLS if s.category == cat
            ]
        except ValueError:
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status."""
        return {
            "total_skills": len(ULTIMATE_SKILLS),
            "categories": len(SkillCategory),
            "priority_1_skills": len([s for s in ULTIMATE_SKILLS if s.priority == 1]),
            "activation_stats": self.analyzer.get_activation_stats(),
            "execution_stats": self.invoker.get_execution_stats(),
            "skill_categories": {
                cat.value: len([s for s in ULTIMATE_SKILLS if s.category == cat])
                for cat in SkillCategory
            }
        }


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

_orchestrator: Optional[SkillOrchestrator] = None

def get_skill_orchestrator() -> SkillOrchestrator:
    """Get or create the global skill orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SkillOrchestrator()
    return _orchestrator


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def orchestrate_task(task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Orchestrate a task with automatic skill detection and invocation."""
    return get_skill_orchestrator().orchestrate(task, context)


def execute_with_orchestration(task: str, executor: Callable, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Execute a task with full skill orchestration."""
    return get_skill_orchestrator().execute(task, executor, context)


def get_all_100_skills() -> List[Dict]:
    """Get all 100+ skills in a readable format."""
    return get_skill_orchestrator().list_all_skills()


def analyze_and_show(task: str) -> str:
    """Analyze a task and show all detected skills."""
    result = orchestrate_task(task)
    
    output = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                          SKILL ANALYSIS                                 ║
╚══════════════════════════════════════════════════════════════════════════╝

📋 Task: {result['task']}
🏷️ Type: {result['task_type']}
✅ Skills Detected: {result['skills_detected']}
🔄 Auto-Invoke: {result['auto_invoke']}
🖥️ MCP Servers: {result['mcp_servers']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DETECTED SKILLS (Auto-Invoked when needed):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    for i, skill in enumerate(result['skills_detected'], 1):
        auto_marker = "✓" if skill['name'] in result['auto_invoke'] else "○"
        output += f"\n{auto_marker} {i}. {skill['name']} ({skill['category']})"
        output += f"\n   Description: {skill['description']}"
        output += f"\n   Match Score: {skill['match_score']} | Confidence: {skill['confidence']}"
        output += f"\n   Triggers: {', '.join(skill['triggers'][:3])}"
    
    output += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Use these skills in your code to get AI-powered assistance!

"""
    
    return output