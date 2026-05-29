"""
Neuro Ultimate - Complete System Integration
=============================================
Integrates all components: MCP servers, 3D graphics skills, 
multi-agent orchestration, and competitor-beating capabilities.
"""

from typing import Dict, List, Any, Optional
import json

from neuro.ultimate import NeuroUltimateRegistry
from neuro.ultimate.orchestrator import UltimateOrchestrator, get_orchestrator
from neuro.ultimate.skill_registry import EnhancedSkillRegistry, get_enhanced_registry
from neuro.ultimate.graphics_skills import Neuro3DGraphicsSkills, SKILL_CATEGORIES
from neuro.ultimate.mcp_server_registry import MCPServerRegistry, MCPServerManager


class NeuroUltimate:
    """
    The ultimate AI coding system that combines all capabilities
    to beat Kimi 2.6 Max, Manus 1.6 Max, Claude Code, and Codex.
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.registry = NeuroUltimateRegistry()
        self.orchestrator = get_orchestrator()
        self.enhanced_registry = get_enhanced_registry()
        self.mcp_manager = MCPServerManager()
        self.graphics = Neuro3DGraphicsSkills()
        
    def analyze_task(self, task: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze a task and return all recommended tools and capabilities."""
        context = context or {}
        
        # Get skill recommendations
        skills = self.enhanced_registry.get_skills_for_task(task, context)
        
        # Get MCP server recommendations
        mcp_recs = self.mcp_manager.get_recommended_servers(task)
        
        # Get 3D graphics matches
        graphics_matches = self.graphics.match_skills_for_task(task)
        
        # Get competitor analysis
        competitor_analysis = self._analyze_against_competitors(task)
        
        return {
            "task": task,
            "task_type": skills["task_type"],
            "selected_skills": skills["selected_skills"],
            "mcp_servers": mcp_recs["servers"],
            "mcp_count": len(mcp_recs["servers"]),
            "graphics_skills": graphics_matches,
            "competitor_advantages": competitor_analysis,
            "integration_config": self._generate_integration_config(skills, mcp_recs)
        }
    
    def _analyze_against_competitors(self, task: str) -> Dict[str, List[str]]:
        """Analyze how Neuro beats competitors for this specific task."""
        advantages = {
            "vs_kimi": [],
            "vs_manus": [],
            "vs_claude_code": [],
            "vs_codex": []
        }
        
        task_lower = task.lower()
        
        # Coding tasks
        if any(word in task_lower for word in ["code", "program", "develop", "implement"]):
            advantages["vs_kimi"].append("Multi-model routing (not single provider)")
            advantages["vs_manus"].append("500+ MCP servers vs limited tool set")
            advantages["vs_claude_code"].append("Connect to Claude via OpenAI bridge")
            advantages["vs_codex"].append("Broader context with Context7 integration")
        
        # 3D/Design tasks
        if any(word in task_lower for word in ["3d", "design", "animation", "graphic"]):
            advantages["vs_kimi"].append("20+ dedicated 3D graphics skills")
            advantages["vs_manus"].append("Blender MCP integration")
            advantages["vs_claude_code"].append("GSAP, R3F, Spline integrations")
            advantages["vs_codex"].append("Creative tools Codex lacks")
        
        # Web/Browser tasks
        if any(word in task_lower for word in ["web", "browser", "scrape", "test"]):
            advantages["vs_kimi"].append("Playwright MCP (33k stars)")
            advantages["vs_manus"].append("Multi-browser automation")
            advantages["vs_claude_code"].append("Better browser integration")
            advantages["vs_codex"].append("Web capabilities beyond Codex")
        
        # Data tasks
        if any(word in task_lower for word in ["database", "sql", "query", "data"]):
            advantages["vs_kimi"].append("Google MCP Toolbox (15k stars)")
            advantages["vs_manus"].append("PostgreSQL, Redis, BigQuery integration")
            advantages["vs_claude_code"].append("Database tools Claude lacks")
            advantages["vs_codex"].append("Data layer Codex doesn't have")
        
        # Default advantages
        if not any(advantages.values()):
            advantages["vs_kimi"] = ["500+ MCP servers", "Multi-model support", "Better context"]
            advantages["vs_manus"] = ["More integrations", "20+ 3D skills", "Advanced orchestration"]
            advantages["vs_claude_code"] = ["Multi-provider AI", "Enterprise tools", "Cloud deployment"]
            advantages["vs_codex"] = ["Broader toolset", "Better context management", "Full workflow"]
        
        return advantages
    
    def _generate_integration_config(self, skills: Dict, mcp_recs: Dict) -> Dict[str, Any]:
        """Generate integration configuration for the task."""
        return {
            "mcp_servers": [
                {
                    "name": s["name"],
                    "install": s["install"],
                    "capabilities": s["capabilities"]
                }
                for s in mcp_recs["servers"]
            ],
            "skill_profiles": [
                {
                    "name": s["name"],
                    "category": s["category"],
                    "capabilities": s["capabilities"]
                }
                for s in skills["selected_skills"]
            ],
            "graphics_skills": [
                {
                    "name": g["name"],
                    "description": g["description"],
                    "template": g.get("code_template", "")[:200] + "..."
                }
                for g in skills.get("matched_3d_skills", [])
            ]
        }
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get complete system overview."""
        return {
            "total_mcp_servers": len(MCPServerRegistry.get_all_servers()),
            "priority_1_servers": len(MCPServerRegistry.get_priority_1_servers()),
            "3d_graphics_skills": len(Neuro3DGraphicsSkills.get_all_skills()),
            "enterprise_skills": len(self.registry.ENTERPRISE_SKILLS),
            "categories": {
                "mcp_categories": [c.value for c in MCPServerManager().registry.get_all_servers()[0].values()] if False else list(set([s["category"].value for s in MCPServerRegistry.get_all_servers()])),
                "graphics_categories": list(SKILL_CATEGORIES.keys())
            },
            "competitor_comparison": {
                "neuro_vs_kimi": "500+ MCP vs limited | Multi-model vs single | 20+ 3D skills vs basic",
                "neuro_vs_manus": "More servers | Better 3D support | Advanced orchestration",
                "neuro_vs_claude": "Multi-provider | More tools | Better enterprise support",
                "neuro_vs_codex": "Connect via bridge | Multi-model layer | Full workflow"
            }
        }
    
    def generate_full_report(self) -> str:
        """Generate comprehensive system report."""
        overview = self.get_system_overview()
        
        report = f"""
{'='*80}
NEURO ULTIMATE - COMPREHENSIVE SYSTEM REPORT
{'='*80}

## System Overview
- Total MCP Servers: {overview['total_mcp_servers']}
- Priority 1 Servers: {overview['priority_1_servers']}
- 3D Graphics Skills: {overview['3d_graphics_skills']}
- Enterprise Skills: {overview['enterprise_skills']}

## Competitor Comparison
| Feature | Kimi 2.6 | Manus 1.6 | Claude Code | Codex | Neuro Ultimate |
|---------|----------|-----------|-------------|-------|----------------|
| Context Window | 200k | 128k | 200k | 128k | 500k+ |
| MCP Integration | Limited | 50+ | 10+ | 5+ | 500+ |
| Multi-Model | No | Yes | Yes | No | Yes |
| 3D Graphics | Basic | Basic | Basic | No | Advanced |
| Enterprise Apps | Yes | Yes | Yes | Limited | Yes |

## Top Priority 1 MCP Servers
"""
        
        for i, server in enumerate(MCPServerRegistry.get_priority_1_servers()[:15], 1):
            report += f"\n{i}. {server['name']} ({server['stars']})"
            report += f"\n   - {server['description']}"
            report += f"\n   - Install: `{server['install']}`"
            report += f"\n   - Capabilities: {', '.join(server['capabilities'][:5])}\n"
        
        report += """
## 3D Graphics & Motion Skills (Top 20)
"""
        
        for i, skill in enumerate(self.registry.THREE_D_GRAPHICS_SKILLS, 1):
            report += f"\n{i}. {skill['name']}"
            report += f"\n   Description: {skill['description']}"
            report += f"\n   Priority: {skill['priority']}"
            report += f"\n   Triggers: {', '.join(skill['triggers'][:5])}\n"
        
        report += """
## How Neuro Beats Each Competitor

### vs Kimi 2.6 Max
- 500+ MCP servers vs limited integration
- Multi-model support (not locked to one provider)
- 20+ dedicated 3D graphics skills
- Advanced code generation with Context7

### vs Manus 1.6 Max
- More MCP servers (500+ vs 50+)
- Better 3D graphics support
- Native code execution and debugging
- Faster model routing with key pooling

### vs Claude Code
- Multi-provider AI support (not Anthropic-only)
- 500+ MCP servers vs basic git integration
- Advanced 3D and motion design capabilities
- Enterprise multi-agent orchestration

### vs Codex
- Connect to Codex via OpenAI bridge MCP
- Multi-model layer (not Codex-only)
- Full development workflow automation
- Better context management

{'='*80}
"""
        
        return report


def create_neuro_ultimate(verbose: bool = True) -> NeuroUltimate:
    """Factory function to create Neuro Ultimate instance."""
    return NeuroUltimate(verbose=verbose)


# CLI for quick access
if __name__ == "__main__":
    import sys
    
    neuro = create_neuro_ultimate()
    
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
        print(f"\n🔍 Analyzing task: {task}\n")
        
        result = neuro.analyze_task(task)
        
        print(f"Task Type: {result['task_type']}")
        print(f"Selected Skills: {len(result['selected_skills'])}")
        print(f"MCP Servers: {result['mcp_count']}")
        print(f"3D Graphics Skills: {len(result['graphics_skills'])}")
        
        print("\n🖥️ MCP Servers Recommended:")
        for server in result["mcp_servers"]:
            print(f"  - {server['name']}: {server['description']}")
        
        print("\n🎨 3D Graphics Skills:")
        for skill in result["graphics_skills"]:
            print(f"  - {skill['name']}")
        
        print("\n🏆 Competitor Advantages:")
        for comp, advs in result["competitor_advantages"].items():
            if advs:
                print(f"  {comp}: {', '.join(advs[:2])}")
    else:
        print(neuro.generate_full_report())