"""
Skill Middleware for Smart Router
Intercepts and enhances LLM calls with skill context
"""

from typing import Dict, List, Any, Optional, Callable
from functools import wraps


class SkillMiddleware:
    """
    Middleware that intercepts router calls and enriches prompts with skill context.
    This ensures skills are used throughout the LLM call lifecycle.
    """
    
    def __init__(self):
        self.enabled = True
        self.active_skills: List[str] = []
        self.skill_context: Dict[str, Any] = {}
        self._pre_hooks: List[Callable] = []
        self._post_hooks: List[Callable] = []
    
    def set_skills(self, skills: List[str], context: Dict[str, Any] = None):
        """Set active skills and context."""
        self.active_skills = skills
        self.skill_context = context or {}
    
    def add_pre_hook(self, hook: Callable):
        """Add a pre-processing hook."""
        self._pre_hooks.append(hook)
    
    def add_post_hook(self, hook: Callable):
        """Add a post-processing hook."""
        self._post_hooks.append(hook)
    
    def preprocess(self, messages: List[Dict], context: Dict[str, Any] = None) -> List[Dict]:
        """
        Pre-process messages before sending to LLM.
        Adds skill context to system message.
        """
        if not self.enabled:
            return messages
        
        # Run pre-hooks
        for hook in self._pre_hooks:
            messages = hook(messages, self.active_skills, self.skill_context) or messages
        
        # Add skill context to system message if not already there
        if self.active_skills and messages:
            system_msg = messages[0] if messages[0].get("role") == "system" else None
            
            skill_section = self._build_skill_section()
            
            if system_msg:
                # Append to existing system message
                if "AVAILABLE SKILLS" not in system_msg["content"]:
                    system_msg["content"] += skill_section
            else:
                # Create new system message
                messages.insert(0, {
                    "role": "system",
                    "content": f"You are Neuro, an expert AI with access to skills.\n{skill_section}"
                })
        
        return messages
    
    def postprocess(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post-process LLM response.
        Can add skill metadata or transform response.
        """
        if not self.enabled:
            return response
        
        # Run post-hooks
        for hook in self._post_hooks:
            response = hook(response, self.active_skills, self.skill_context) or response
        
        # Add skill metadata to response
        if "metadata" not in response:
            response["metadata"] = {}
        
        response["metadata"]["skills_used"] = self.active_skills
        response["metadata"]["skill_count"] = len(self.active_skills)
        
        return response
    
    def _build_skill_section(self) -> str:
        """Build the skill context section for prompts."""
        if not self.active_skills:
            return ""
        
        lines = [
            "\n\n=== AVAILABLE SKILLS ===",
            "You have access to these specialized skills:",
        ]
        
        # Categorize skills
        categories = {
            "Code Quality": ["code-review", "code-simplifier", "add-javadoc", "security"],
            "Version Control": ["github", "gitlab", "bitbucket", "iterate"],
            "DevOps": ["docker", "kubernetes", "vercel", "azure-devops"],
            "Data/ML": ["jupyter", "spark-version-upgrade", "datadog"],
            "Frontend": ["frontend-design", "theme-factory"],
            "Communication": ["slack", "discord", "notion", "linear"],
            "Memory": ["agent_memory", "swarmvault", "memory"],
            "Automation": ["browser_automation", "playwright", "mcp_integration"],
        }
        
        for skill in self.active_skills:
            for cat, skills in categories.items():
                if skill in skills:
                    lines.append(f"- {skill}: {cat}")
                    break
        
        # Add skill hints from context
        if self.skill_context:
            if "endpoint" in self.skill_context:
                lines.append(f"\nMCP Endpoint: {self.skill_context['endpoint']}")
            if "memory_context" in self.skill_context:
                lines.append(f"\nRelevant Memory: {self.skill_context['memory_context'][:200]}...")
        
        lines.append("=== END SKILLS ===\n")
        
        return "\n".join(lines)
    
    def wrap_router_complete(self, router_complete_fn):
        """
        Decorator to wrap router.complete() with skill middleware.
        
        Usage:
            middleware = SkillMiddleware()
            middleware.set_skills(["code-review", "security"])
            
            @middleware.wrap_router_complete
            def my_router_complete(messages, **kwargs):
                return original_complete(messages, **kwargs)
        """
        @wraps(router_complete_fn)
        def wrapped(messages: List[Dict], **kwargs) -> Dict[str, Any]:
            # Pre-process
            processed_messages = self.preprocess(messages, self.skill_context)
            
            # Call original router
            response = router_complete_fn(processed_messages, **kwargs)
            
            # Post-process
            return self.postprocess(response)
        
        return wrapped


# Global middleware instance
_middleware = SkillMiddleware()


def get_middleware() -> SkillMiddleware:
    """Get the global skill middleware instance."""
    return _middleware


def set_active_skills(skills: List[str], context: Dict[str, Any] = None):
    """Set active skills for the global middleware."""
    _middleware.set_skills(skills, context)


def clear_skills():
    """Clear active skills from global middleware."""
    _middleware.set_skills([], {})


def apply_skill_context(messages: List[Dict]) -> List[Dict]:
    """Quick function to apply skill context to messages."""
    return _middleware.preprocess(messages)


def register_skill(name: str, description: str = None, category: str = None):
    """
    Decorator to register a skill with the middleware.
    
    Usage:
        @register_skill("deep_research", "Automated research workflow", category="research")
        def deep_research(...):
            ...
    """
    def decorator(func):
        func._skill_name = name
        func._skill_description = description or func.__doc__ or name
        func._skill_category = category or "general"
        func._skill_registered = True
        return func
    return decorator


def get_registered_skills() -> List[Dict[str, Any]]:
    """Get all skills registered with @register_skill decorator."""
    skills = []
    import neuro.skills
    for attr_name in dir(neuro.skills):
        try:
            attr = getattr(neuro.skills, attr_name)
            if callable(attr) and getattr(attr, '_skill_registered', False):
                skills.append({
                    'name': getattr(attr, '_skill_name', attr_name),
                    'description': getattr(attr, '_skill_description', ''),
                    'category': getattr(attr, '_skill_category', 'general'),
                    'func': attr
                })
        except Exception:
            pass
    return skills


# Export everything for convenience
__all__ = [
    'SkillMiddleware',
    'get_middleware',
    'set_active_skills',
    'clear_skills',
    'apply_skill_context',
    'register_skill',
    'get_registered_skills',
]
