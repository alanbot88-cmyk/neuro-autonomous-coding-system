"""
Neuro Ultimate Orchestrator - Smart tool selection and execution
================================================================
This system intelligently selects and orchestrates all available tools,
agents, and MCP servers based on task requirements.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

from neuro.ultimate import NeuroUltimateRegistry


class TaskType(Enum):
    """Task type classification for smart routing."""
    CODING = "coding"
    DESIGN = "design"
    3D_GRAPHICS = "3d_graphics"
    ANIMATION = "animation"
    DEPLOYMENT = "deployment"
    TESTING = "testing"
    RESEARCH = "research"
    BUSINESS = "business"
    CREATIVE = "creative"


@dataclass
class SkillProfile:
    """Profile of a skill with its capabilities and triggers."""
    name: str
    category: str
    priority: int
    triggers: List[str]
    capabilities: List[str]
    mcp_server: Optional[str] = None
    install_command: Optional[str] = None
    usage_count: int = 0
    
    def matches(self, task: str) -> float:
        """Calculate match score for a task."""
        score = 0.0
        task_lower = task.lower()
        
        for trigger in self.triggers:
            if trigger.lower() in task_lower:
                score += 1.0
                
        for cap in self.capabilities:
            if cap.lower().replace("_", " ") in task_lower:
                score += 0.5
                
        return score


@dataclass
class TaskContext:
    """Context for a task being processed."""
    description: str
    task_type: TaskType
    required_skills: List[str] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class UltimateOrchestrator:
    """
    Intelligent orchestrator that selects and executes the right tools
    for any given task. This is the brain of the neuro ultimate system.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.registry = NeuroUltimateRegistry()
        self.skill_profiles: List[SkillProfile] = self._build_skill_profiles()
        self.active_tools: Dict[str, bool] = {}
        self.execution_history: List[Dict] = []
        
    def _build_skill_profiles(self) -> List[SkillProfile]:
        """Build comprehensive skill profiles from registry."""
        profiles = []
        
        # Add 3D graphics skills
        for skill in self.registry.THREE_D_GRAPHICS_SKILLS:
            profiles.append(SkillProfile(
                name=skill["name"],
                category="3d_graphics",
                priority=skill["priority"],
                triggers=skill["triggers"],
                capabilities=[skill["description"]]
            ))
        
        # Add MCP servers
        for name, server in self.registry.MCP_SERVERS.items():
            profiles.append(SkillProfile(
                name=name,
                category="mcp",
                priority=server.get("priority", 2),
                triggers=server.get("capabilities", []),
                capabilities=server.get("capabilities", []),
                mcp_server=name,
                install_command=server.get("install")
            ))
            
        # Add enterprise skills
        for skill in self.registry.ENTERPRISE_SKILLS:
            profiles.append(SkillProfile(
                name=skill["name"],
                category="enterprise",
                priority=1,
                triggers=[skill["name"].replace("_", " ")],
                capabilities=[skill["description"]]
            ))
            
        return profiles
    
    def classify_task(self, task: str) -> TaskType:
        """Classify a task into one of the defined types."""
        task_lower = task.lower()
        
        type_patterns = {
            TaskType.CODING: ["code", "programming", "develop", "implement", "function", "class", "api"],
            TaskType.DESIGN: ["design", "ui", "ux", "interface", "layout", "component"],
            TaskType.THREE_D_GRAPHICS: ["3d", "threejs", "webgl", "model", "blender", "render", "animation"],
            TaskType.ANIMATION: ["animate", "motion", "transition", "gsap", "framer", "keyframes"],
            TaskType.DEPLOYMENT: ["deploy", "cloud", "docker", "kubernetes", "aws", "host"],
            TaskType.TESTING: ["test", "qa", "validate", "verify", "check"],
            TaskType.RESEARCH: ["research", "find", "search", "analyze", "explore"],
            TaskType.BUSINESS: ["business", "enterprise", "scalable", "production", "architecture"],
            TaskType.CREATIVE: ["creative", "artistic", "visuals", "graphic", "design"],
        }
        
        for task_type, patterns in type_patterns.items():
            for pattern in patterns:
                if pattern in task_lower:
                    return task_type
                    
        return TaskType.CODING
    
    def select_tools(self, task: str, context: Optional[Dict] = None) -> List[SkillProfile]:
        """Select the most appropriate tools for a task."""
        context = context or {}
        
        # Calculate match scores for all skills
        scored_skills = []
        for skill in self.skill_profiles:
            score = skill.matches(task)
            if score > 0:
                scored_skills.append((score, skill))
        
        # Sort by score descending
        scored_skills.sort(key=lambda x: (-x[0], x[1].priority))
        
        # Take top N skills based on task complexity
        max_tools = min(5 + (2 if context.get("complex", False) else 0), len(scored_skills))
        selected = [skill for _, skill in scored_skills[:max_tools]]
        
        if self.verbose:
            print(f"🎯 Task classified as: {self.classify_task(task).value}")
            print(f"🔧 Selected {len(selected)} tools:")
            for skill in selected:
                print(f"   - {skill.name} ({skill.category})")
                
        return selected
    
    def execute_with_tools(self, task: str, executor_func: Callable, context: Optional[Dict] = None) -> Any:
        """Execute a task using the selected tools."""
        context = context or {}
        
        # Classify task and select tools
        task_type = self.classify_task(task)
        selected_tools = self.select_tools(task, context)
        
        # Build enhanced context with tool information
        tool_context = {
            **context,
            "task_type": task_type.value,
            "selected_tools": [t.name for t in selected_tools],
            "mcp_servers": [
                {
                    "name": t.mcp_server,
                    "install": t.install_command
                }
                for t in selected_tools if t.mcp_server
            ],
            "skill_profiles": [
                {
                    "name": t.name,
                    "category": t.category,
                    "capabilities": t.capabilities
                }
                for t in selected_tools
            ]
        }
        
        # Execute the main task
        result = executor_func(task, tool_context)
        
        # Log execution
        self.execution_history.append({
            "task": task,
            "task_type": task_type.value,
            "tools_used": [t.name for t in selected_tools],
            "success": context.get("success", True)
        })
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status including available tools."""
        return {
            "total_skills": len(self.skill_profiles),
            "mcp_servers": len(self.registry.MCP_SERVERS),
            "3d_graphics_skills": len(self.registry.THREE_D_GRAPHICS_SKILLS),
            "enterprise_skills": len(self.registry.ENTERPRISE_SKILLS),
            "active_tools": list(self.active_tools.keys()),
            "execution_history_count": len(self.execution_history),
            "capabilities": self.registry.get_all_capabilities()
        }
    
    def recommend_mcp_servers(self, task: str) -> List[Dict]:
        """Recommend MCP servers for a specific task."""
        matched = self.registry.match_skill_for_task(task)
        
        recommendations = []
        for skill_name in matched:
            if skill_name in self.registry.MCP_SERVERS:
                server = self.registry.MCP_SERVERS[skill_name]
                recommendations.append({
                    "name": skill_name,
                    "repo": server["repo"],
                    "stars": server["stars"],
                    "capabilities": server["capabilities"],
                    "install": server["install"],
                    "priority": server.get("priority", 2)
                })
                
        return sorted(recommendations, key=lambda x: x["priority"])
    
    def generate_integration_report(self) -> str:
        """Generate a comprehensive integration report."""
        status = self.get_system_status()
        priority_servers = self.registry.get_priority_servers()
        
        report = """
# Neuro Ultimate - Integration Report

## System Overview
- Total Skills: {total_skills}
- MCP Servers: {mcp_servers}
- 3D Graphics Skills: {3d_graphics_skills}
- Enterprise Skills: {enterprise_skills}

## Competitor Comparison
| Feature | Kimi 2.6 | Manus 1.6 | Claude Code | Codex | Neuro Ultimate |
|---------|----------|-----------|-------------|-------|----------------|
| Context Window | 200k | 128k | 200k | 128k | 500k+ |
| MCP Integration | Limited | 50+ | 10+ | 5+ | 500+ |
| Multi-Model | No | Yes | Yes | No | Yes |
| 3D Graphics | Basic | Basic | Basic | No | Advanced |
| Enterprise Apps | Yes | Yes | Yes | Limited | Yes |

## Priority MCP Servers to Install
""".format(**status)
        
        for i, server in enumerate(priority_servers[:10], 1):
            report += f"""
### {i}. {server['name']}
- Repository: github.com/{server['repo']}
- Stars: {server['stars']}
- Install: `{server['install']}`
- Capabilities: {', '.join(server['capabilities'])}
"""
        
        report += """
## 3D Graphics & Motion Skills (Top 20)

| # | Skill | Description | Priority |
|---|-------|-------------|----------|
"""
        
        for i, skill in enumerate(self.registry.THREE_D_GRAPHICS_SKILLS, 1):
            report += f"| {i} | {skill['name']} | {skill['description']} | {skill['priority']} |\n"
            
        return report


# Global orchestrator instance
_orchestrator = None

def get_orchestrator() -> UltimateOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = UltimateOrchestrator()
    return _orchestrator