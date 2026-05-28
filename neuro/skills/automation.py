"""
Neuro Skill Automation System
Automatically triggers skills based on code analysis and task patterns
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

class SkillTriggerType(Enum):
    KEYWORD = "keyword"
    PATTERN = "pattern"
    FILE_TYPE = "file_type"
    CONTEXT = "context"

@dataclass
class SkillTrigger:
    trigger_type: SkillTriggerType
    pattern: str
    skill_names: List[str]

class SkillAutomation:
    """
    Skill automation that auto-triggers based on code patterns
    """
    
    # Define automation triggers - automatically activated when patterns match
    AUTOMATION_TRIGGERS = [
        # GitHub integration
        SkillTrigger(SkillTriggerType.KEYWORD, r"github|git\s+push|git\s+commit|pr|pull\s+request", 
                     ["github", "github-pr-review", "iterate"]),
        
        # Security scanning
        SkillTrigger(SkillTriggerType.KEYWORD, r"security|vulnerability|auth|token|secret|password",
                     ["security"]),
        
        # Code quality
        SkillTrigger(SkillTriggerType.KEYWORD, r"refactor|simplify|clean\s+up|optimize",
                     ["code-simplifier"]),
        
        # Code review
        SkillTrigger(SkillTriggerType.KEYWORD, r"code\s+review|review\s+pr|review\s+code",
                     ["code-review"]),
        
        # Frontend development
        SkillTrigger(SkillTriggerType.KEYWORD, r"frontend|ui|interface|design|component|react|html",
                     ["frontend-design", "theme-factory"]),
        
        # Docker/Container
        SkillTrigger(SkillTriggerType.KEYWORD, r"docker|container|containerize|kubernetes|k8s",
                     ["docker", "kubernetes"]),
        
        # API/Web
        SkillTrigger(SkillTriggerType.KEYWORD, r"api|rest|endpoint|http|server",
                     ["github", "iterate"]),
        
        # Documentation
        SkillTrigger(SkillTriggerType.KEYWORD, r"docs?|documentation|readme|changelog",
                     ["release-notes"]),
        
        # Testing/QA
        SkillTrigger(SkillTriggerType.KEYWORD, r"test|qa|verify|validation|unit\s+test",
                     ["qa-changes", "iterate"]),
        
        # Database
        SkillTrigger(SkillTriggerType.KEYWORD, r"database|sql|migration|schema",
                     ["code-review", "security"]),
        
        # DevOps/CI
        SkillTrigger(SkillTriggerType.KEYWORD, r"ci|cd|pipeline|deploy|automation",
                     ["iterate", "github"]),
        
        # Monitoring
        SkillTrigger(SkillTriggerType.KEYWORD, r"monitor|metrics|log|alert",
                     ["datadog"]),
        
        # Communication
        SkillTrigger(SkillTriggerType.KEYWORD, r"slack|discord|notification|message",
                     ["slack-channel-monitor", "discord"]),
        
        # Project management
        SkillTrigger(SkillTriggerType.KEYWORD, r"linear|issue|ticket|task",
                     ["linear"]),
        
        # Documentation tools
        SkillTrigger(SkillTriggerType.KEYWORD, r"notion|wiki|document",
                     ["notion"]),
        
        # Jupyter/Data science
        SkillTrigger(SkillTriggerType.KEYWORD, r"jupyter|notebook|data\s+science|ml|ai",
                     ["jupyter"]),
        
        # SDK/Agent development
        SkillTrigger(SkillTriggerType.KEYWORD, r"sdk|agent|openhands|llm",
                     ["openhands-sdk", "agent-sdk-builder", "agent-creator"]),
    ]
    
    @classmethod
    def analyze_task(cls, task: str, context: Dict[str, Any] = None) -> List[str]:
        """Analyze task and return matching skill names"""
        matched_skills = set()
        task_lower = task.lower()
        
        for trigger in cls.AUTOMATION_TRIGGERS:
            if trigger.trigger_type == SkillTriggerType.KEYWORD:
                if re.search(trigger.pattern, task_lower, re.IGNORECASE):
                    matched_skills.update(trigger.skill_names)
        
        return list(matched_skills)
    
    @classmethod
    def get_context_skills(cls, context: Dict[str, Any]) -> List[str]:
        """Get skills based on execution context"""
        skills = []
        
        # File-based context
        if "file_path" in context:
            path = context["file_path"]
            ext = Path(path).suffix.lower()
            
            file_skill_map = {
                ".py": ["code-review", "code-simplifier"],
                ".js": ["code-review", "code-simplifier", "frontend-design"],
                ".ts": ["code-review", "code-simplifier", "frontend-design"],
                ".jsx": ["frontend-design", "code-review"],
                ".tsx": ["frontend-design", "code-review"],
                ".go": ["code-review", "code-simplifier"],
                ".java": ["code-review", "add-javadoc"],
                ".md": ["release-notes"],
                ".dockerfile": ["docker"],
                ".yml": ["kubernetes"],
                ".yaml": ["kubernetes"],
            }
            
            skills.extend(file_skill_map.get(ext, []))
        
        # Error-based context
        if "error" in context:
            error_str = str(context["error"]).lower()
            if "security" in error_str or "auth" in error_str:
                skills.append("security")
            if "test" in error_str or "assertion" in error_str:
                skills.append("qa-changes")
        
        return list(set(skills))
    
    @classmethod
    def auto_trigger(cls, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main entry point - automatically determine which skills to use
        Returns dict with skills and recommendations
        """
        context = context or {}
        skills = set()
        
        # Task-based skills
        skills.update(cls.analyze_task(task, context))
        
        # Context-based skills
        skills.update(cls.get_context_skills(context))
        
        return {
            "task": task,
            "detected_skills": list(skills),
            "context": context,
            "ready": len(skills) > 0
        }