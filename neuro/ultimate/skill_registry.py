"""
Neuro Enhanced Skill Registry - Complete integration of all skills
===================================================================
Integrates 500+ MCP servers, 50+ AI models, and 20+ 3D graphics skills
for the ultimate autonomous coding system.
"""

from typing import Dict, List, Any, Optional
from neuro.ultimate import NeuroUltimateRegistry, TaskType
from neuro.ultimate.orchestrator import UltimateOrchestrator, get_orchestrator


# =============================================================================
# ENHANCED SKILL REGISTRY
# =============================================================================

class EnhancedSkillRegistry:
    """
    Enhanced skill registry that provides intelligent skill matching,
    tool orchestration, and MCP server integration.
    """
    
    def __init__(self):
        self.registry = NeuroUltimateRegistry()
        self.orchestrator = get_orchestrator()
        self._skill_cache: Dict[str, List[str]] = {}
        
    def register_skill(self, name: str, capability: str, triggers: List[str]):
        """Register a new skill dynamically."""
        if not hasattr(self.registry, 'custom_skills'):
            self.registry.custom_skills = []
            
        self.registry.custom_skills.append({
            "name": name,
            "capability": capability,
            "triggers": triggers
        })
        
    def get_skills_for_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Get all relevant skills for a task."""
        context = context or {}
        
        # Use orchestrator to classify and select tools
        selected_tools = self.orchestrator.select_tools(task, context)
        
        # Build skill response
        response = {
            "task_type": self.orchestrator.classify_task(task).value,
            "selected_skills": [
                {
                    "name": tool.name,
                    "category": tool.category,
                    "capabilities": tool.capabilities,
                    "mcp_server": tool.mcp_server,
                    "install_command": tool.install_command
                }
                for tool in selected_tools
            ],
            "mcp_servers": self.orchestrator.recommend_mcp_servers(task),
            "matched_3d_skills": self._match_3d_skills(task),
            "matched_enterprise_skills": self._match_enterprise_skills(task)
        }
        
        return response
    
    def _match_3d_skills(self, task: str) -> List[Dict]:
        """Match 3D graphics skills for a task."""
        matched = []
        task_lower = task.lower()
        
        for skill in self.registry.THREE_D_GRAPHICS_SKILLS:
            for trigger in skill["triggers"]:
                if trigger.lower() in task_lower:
                    matched.append(skill)
                    break
                    
        return matched
    
    def _match_enterprise_skills(self, task: str) -> List[Dict]:
        """Match enterprise skills for a task."""
        matched = []
        task_lower = task.lower()
        
        for skill in self.registry.ENTERPRISE_SKILLS:
            if skill["name"].replace("_", " ") in task_lower:
                matched.append(skill)
            elif any(word in task_lower for word in skill["description"].split()):
                matched.append(skill)
                
        return matched
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """Get MCP server configuration for all registered servers."""
        config = {
            "mcpServers": {}
        }
        
        for name, server in self.registry.MCP_SERVERS.items():
            if server.get("priority", 2) <= 1:
                # Format for Claude Desktop or other MCP clients
                install = server.get("install", "")
                
                # Extract npm/pip package from install command
                if "npx" in install:
                    package = install.split("npx -y")[-1].strip()
                    config["mcpServers"][name] = {
                        "command": "npx",
                        "args": ["-y", package]
                    }
                elif "pip" in install:
                    package = install.split("pip install")[-1].strip()
                    config["mcpServers"][name] = {
                        "command": "python",
                        "args": ["-m", "mcp", "install", package]
                    }
                elif "npm" in install:
                    package = install.split("npm install -g")[-1].strip()
                    config["mcpServers"][name] = {
                        "command": "npm",
                        "args": ["-g", package]
                    }
                    
        return config


# Global enhanced registry instance
_enhanced_registry = None

def get_enhanced_registry() -> EnhancedSkillRegistry:
    """Get or create the global enhanced registry instance."""
    global _enhanced_registry
    if _enhanced_registry is None:
        _enhanced_registry = EnhancedSkillRegistry()
    return _enhanced_registry


# =============================================================================
# SKILL EXECUTION HELPERS
# =============================================================================

class SkillExecutor:
    """Execute skills with proper context and error handling."""
    
    def __init__(self):
        self.registry = get_enhanced_registry()
        self.orchestrator = get_orchestrator()
        
    def execute_task(self, task: str, executor_fn, context: Optional[Dict] = None) -> Any:
        """Execute a task with automatic skill selection."""
        return self.orchestrator.execute_with_tools(task, executor_fn, context)
    
    def generate_mcp_setup_script(self) -> str:
        """Generate a shell script to set up all MCP servers."""
        servers = self.registry.registry.get_priority_servers()
        
        script = """#!/bin/bash
# Neuro Ultimate - MCP Server Setup Script
# Generated automatically

set -e

echo "🚀 Setting up Neuro Ultimate MCP Servers..."

"""
        
        for server in servers:
            install = server.get("install", "")
            name = server["name"]
            script += f'''
echo "Installing {name}..."
{install}
'''
            
        script += """
echo "✅ All MCP servers installed successfully!"
"""
        
        return script
    
    def generate_docker_compose(self) -> str:
        """Generate docker-compose.yml for MCP servers."""
        return '''version: '3.8'

services:
  # ActivePieces - Workflow Automation
  activepieces:
    image: activepieces/activepieces
    ports:
      - "3000:3000"
    environment:
      - AP_QUEUE_CONCURRENCY=5
      - AP_JWT_SECRET=neuro-ultimate-secret

  # Casdoor - Authentication & IAM
  casdoor:
    image: casbin/casdoor
    ports:
      - "8000:8000"
    environment:
      - RUN_IN_DOCKER=true

  # Context7 - Code Context Retrieval
  context7:
    image: context7/context7-server
    ports:
      - "3001:3001"

  # Memory MCP - Persistent Context
  memory:
    image: memory/mcp-memory
    ports:
      - "3002:3002"

volumes:
  activepieces_data:
  casdoor_data:
'''


# =============================================================================
# COMPETITOR COMPARISON TOOLS
# =============================================================================

class CompetitorAnalyzer:
    """Analyze and compare against competitor systems."""
    
    def __init__(self):
        self.registry = NeuroUltimateRegistry()
        
    def generate_comparison_report(self) -> Dict[str, Any]:
        """Generate detailed comparison with competitors."""
        return {
            "neuro_ultimate": {
                "mcp_servers": len(self.registry.MCP_SERVERS),
                "3d_graphics_skills": len(self.registry.THREE_D_GRAPHICS_SKILLS),
                "enterprise_skills": len(self.registry.ENTERPRISE_SKILLS),
                "ai_models": 50,
                "context_window": "500k+ tokens",
                "features": [
                    "Multi-provider LLM support",
                    "Smart tool orchestration",
                    "3D graphics & motion design",
                    "Enterprise-grade architecture",
                    "Automated testing & deployment",
                    "Persistent memory & learning",
                    "GitHub/GitLab integration",
                    "Browser automation",
                    "Database integration",
                    "Cloud deployment"
                ]
            },
            "competitors": self.registry.COMPETITOR_FEATURES
        }
    
    def get_advantage(self, competitor: str) -> List[str]:
        """Get Neuro's advantages over a specific competitor."""
        adv = []
        
        if competitor == "kimi":
            adv = [
                "500+ MCP servers vs limited integration",
                "Multi-model support (not just one provider)",
                "Advanced 3D graphics capabilities",
                "Full IDE integration with context awareness"
            ]
        elif competitor == "manus":
            adv = [
                "More MCP servers (500+ vs 50+)",
                "Better 3D graphics support (20 dedicated skills)",
                "Native code execution and debugging",
                "Faster model routing with key pooling"
            ]
        elif competitor == "claude_code":
            adv = [
                "Multi-provider AI support (not Anthropic-only)",
                "500+ MCP servers vs basic git integration",
                "Advanced 3D and motion design capabilities",
                "Enterprise multi-agent orchestration"
            ]
        elif competitor == "codex":
            adv = [
                "Connect to Codex via OpenAI bridge MCP",
                "Multi-model layer (not Codex-only)",
                "Full development workflow automation",
                "Better context management"
            ]
            
        return adv