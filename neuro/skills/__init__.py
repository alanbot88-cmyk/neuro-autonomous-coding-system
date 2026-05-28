"""
Neuro Skill Manager - Automatic skill utilization system
Auto-loads and auto-triggers skills based on task context
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

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
