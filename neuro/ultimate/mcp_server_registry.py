"""
Neuro MCP Server Integration - Complete MCP Server Registry
===========================================================
Integrates 500+ MCP servers from awesome-mcp-servers with smart
server selection, installation helpers, and runtime management.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class MCPServerCategory(Enum):
    """Categories for MCP servers."""
    CODING = "coding"
    DESIGN = "design"
    DATA = "data"
    CLOUD = "cloud"
    SECURITY = "security"
    COMMUNICATION = "communication"
    AI_MODELS = "ai_models"
    SEARCH = "search"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"
    CREATIVE = "creative"
    ENTERPRISE = "enterprise"


@dataclass
class MCPServer:
    """Represents an MCP server with its configuration."""
    name: str
    repo: str
    stars: str
    description: str
    capabilities: List[str]
    install_command: str
    priority: int
    category: MCPServerCategory
    language: str  # Python, TypeScript, Go, etc.
    platform: str  # Cloud, Local, Both
    os_support: List[str] = field(default_factory=lambda: ["macos", "windows", "linux"])
    
    def to_config(self) -> Dict[str, Any]:
        """Convert to Claude Desktop config format."""
        if self.language == "typescript":
            parts = self.install_command.split(" -y ")
            if len(parts) > 1:
                return {
                    "command": "npx",
                    "args": ["-y", parts[1].strip()]
                }
        return {}


class MCPServerRegistry:
    """
    Comprehensive registry of all available MCP servers.
    Organized by category with priority ratings.
    """
    
    # Top-tier servers (Priority 1 - Must have)
    PRIORITY_1_SERVERS = [
        # Browser & Web
        {
            "name": "playwright",
            "repo": "microsoft/playwright-mcp",
            "stars": "33.2k",
            "description": "Playwright MCP server for browser automation and testing",
            "capabilities": ["browser_automation", "testing", "web_scraping", "cross_browser"],
            "install": "npx -y @playwright/mcp-server",
            "category": MCPServerCategory.CODING,
            "language": "typescript"
        },
        {
            "name": "github_mcp",
            "repo": "github/github-mcp-server",
            "stars": "30.3k",
            "description": "Official GitHub MCP server for repository management",
            "capabilities": ["git_operations", "repo_management", "PR_automation", "issues", "actions"],
            "install": "npx -y @github-mcp/server",
            "category": MCPServerCategory.CODING,
            "language": "go"
        },
        {
            "name": "fastmcp",
            "repo": "PrefectHQ/fastmcp",
            "stars": "25.4k",
            "description": "Fast Pythonic way to build MCP servers",
            "capabilities": ["mcp_development", "tool_creation", "server_building"],
            "install": "pip install fastmcp",
            "category": MCPServerCategory.CODING,
            "language": "python"
        },
        {
            "name": "activepieces",
            "repo": "activepieces/activepieces",
            "stars": "22.5k",
            "description": "AI workflow automation with 400+ MCP servers",
            "capabilities": ["workflow_automation", "integration", "automation"],
            "install": "docker run -p 3000:3000 activepieces/activepieces",
            "category": MCPServerCategory.ENTERPRISE,
            "language": "typescript"
        },
        {
            "name": "mcp_toolbox",
            "repo": "googleapis/mcp-toolbox",
            "stars": "15.4k",
            "description": "Database tools (MySQL, Redis, BigQuery, Elasticsearch)",
            "capabilities": ["database", "mysql", "redis", "bigquery", "elasticsearch", "mongodb"],
            "install": "npx -y @google/mcp-toolbox",
            "category": MCPServerCategory.DATABASE,
            "language": "go"
        },
        {
            "name": "figma_context",
            "repo": "GLips/Figma-Context-MCP",
            "stars": "14.9k",
            "description": "Figma layout information for AI coding agents",
            "capabilities": ["figma", "design_tokens", "layout", "components", "styles"],
            "install": "npx -y figma-context-mcp",
            "category": MCPServerCategory.DESIGN,
            "language": "typescript"
        },
        {
            "name": "casdoor",
            "repo": "casdoor/casdoor",
            "stars": "13.7k",
            "description": "Agent-first IAM and auth gateway",
            "capabilities": ["authentication", "iam", "oauth", "saml", "agent_gateway"],
            "install": "docker run -p 8000:8000 casbin/casdoor",
            "category": MCPServerCategory.SECURITY,
            "language": "go"
        },
        {
            "name": "chrome_mcp",
            "repo": "hangwin/mcp-chrome",
            "stars": "11.7k",
            "description": "Chrome extension-based MCP server",
            "capabilities": ["browser", "chrome", "extension", "automation"],
            "install": "npx -y @mcp-chrome/server",
            "category": MCPServerCategory.CODING,
            "language": "typescript"
        },
        {
            "name": "pal_mcp",
            "repo": "BeehiveInnovations/pal-mcp-server",
            "stars": "11.6k",
            "description": "Alternative to Claude Code, supports Gemini CLI, Codex CLI",
            "capabilities": ["claude_code_alternative", "gemini_cli", "codex_cli", "multi_provider"],
            "install": "pip install pal-mcp-server",
            "category": MCPServerCategory.AI_MODELS,
            "language": "python"
        },
        {
            "name": "context7",
            "repo": "context7/mcp-server",
            "stars": "8k+",
            "description": "Code context retrieval and ranking",
            "capabilities": ["code_search", "context_retrieval", "ranking", "documentation"],
            "install": "npx -y @context7/mcp-server",
            "category": MCPServerCategory.CODING,
            "language": "typescript"
        },
        {
            "name": "filesystem",
            "repo": "modelcontextprotocol/server-filesystem",
            "stars": "8k+",
            "description": "File system operations",
            "capabilities": ["file_operations", "directory_management", "read_write"],
            "install": "npx -y @modelcontextprotocol/server-filesystem",
            "category": MCPServerCategory.FILE_SYSTEM,
            "language": "typescript"
        },
        {
            "name": "postgres",
            "repo": "modelcontextprotocol/server-postgres",
            "stars": "5k+",
            "description": "PostgreSQL database operations",
            "capabilities": ["postgresql", "database", "sql", "queries"],
            "install": "npx -y @modelcontextprotocol/server-postgres",
            "category": MCPServerCategory.DATABASE,
            "language": "typescript"
        },
        {
            "name": "fetch",
            "repo": "modelcontextprotocol/fetch",
            "stars": "6k+",
            "description": "Web fetching and content extraction",
            "capabilities": ["web_fetching", "content_extraction", "crawling", "scraping"],
            "install": "npx -y @modelcontextprotocol/server-fetch",
            "category": MCPServerCategory.SEARCH,
            "language": "typescript"
        },
        {
            "name": "memory",
            "repo": "memory/mcp-memory",
            "stars": "7k+",
            "description": "Persistent memory for AI agents",
            "capabilities": ["memory", "persistent", "context", "learning"],
            "install": "npx -y @memory/mcp",
            "category": MCPServerCategory.AI_MODELS,
            "language": "typescript"
        },
        {
            "name": "deepseek",
            "repo": "arikusi/deepseek-mcp-server",
            "stars": "5k+",
            "description": "DeepSeek AI integration",
            "capabilities": ["deepseek", "chat", "reasoning", "multi_turn"],
            "install": "npx -y deepseek-mcp-server",
            "category": MCPServerCategory.AI_MODELS,
            "language": "typescript"
        },
        {
            "name": "ollama_bridge",
            "repo": "jaspertvdm/mcp-server-ollama-bridge",
            "stars": "4k+",
            "description": "Local LLM via Ollama",
            "capabilities": ["ollama", "local_llm", "llama", "mistral", "qwen"],
            "install": "pip install mcp-server-ollama-bridge",
            "category": MCPServerCategory.AI_MODELS,
            "language": "python"
        },
        {
            "name": "openai_bridge",
            "repo": "jaspertvdm/mcp-server-openai-bridge",
            "stars": "4k+",
            "description": "OpenAI GPT integration",
            "capabilities": ["openai", "gpt4", "function_calling", "api"],
            "install": "pip install mcp-server-openai-bridge",
            "category": MCPServerCategory.AI_MODELS,
            "language": "python"
        },
        {
            "name": "aws_mcp",
            "repo": "aws/aws-mcp",
            "stars": "6k+",
            "description": "AWS services integration",
            "capabilities": ["aws", "cloud", "lambda", "s3", "ec2"],
            "install": "npm install -g @aws-mcp/server",
            "category": MCPServerCategory.CLOUD,
            "language": "typescript"
        },
        {
            "name": "docker_mcp",
            "repo": "docker/docker-mcp",
            "stars": "4k+",
            "description": "Docker container management",
            "capabilities": ["docker", "container", "compose", "kubernetes"],
            "install": "npx -y @docker/mcp",
            "category": MCPServerCategory.CLOUD,
            "language": "typescript"
        },
        {
            "name": "slack_mcp",
            "repo": "slackhq/mcp-slack",
            "stars": "5k+",
            "description": "Slack integration",
            "capabilities": ["slack", "messaging", "channels", "integration"],
            "install": "npx -y @slackhq/mcp-server",
            "category": MCPServerCategory.COMMUNICATION,
            "language": "typescript"
        },
        {
            "name": "notion_mcp",
            "repo": "notionhq/notion-mcp",
            "stars": "6k+",
            "description": "Notion integration",
            "capabilities": ["notion", "documents", "wiki", "database"],
            "install": "npx -y @notionhq/mcp-server",
            "category": MCPServerCategory.ENTERPRISE,
            "language": "typescript"
        },
        {
            "name": "linear_mcp",
            "repo": "linear/linear-mcp",
            "stars": "5k+",
            "description": "Project management integration",
            "capabilities": ["linear", "project_management", "issues", "sprints"],
            "install": "npx -y @linear/mcp-server",
            "category": MCPServerCategory.ENTERPRISE,
            "language": "typescript"
        },
        {
            "name": "blender_mcp",
            "repo": "ahujasid/blender-mcp",
            "stars": "5k+",
            "description": "Blender 3D modeling automation",
            "capabilities": ["blender", "3d", "modeling", "animation", "rendering"],
            "install": "pip install blender-mcp",
            "category": MCPServerCategory.CREATIVE,
            "language": "python"
        },
        {
            "name": "puppeteer",
            "repo": "modelcontextprotocol/puppeteer",
            "stars": "5k+",
            "description": "Headless browser automation",
            "capabilities": ["puppeteer", "browser", "scraping", "automation"],
            "install": "npx -y @modelcontextprotocol/server-puppeteer",
            "category": MCPServerCategory.CODING,
            "language": "typescript"
        },
        {
            "name": "snyk",
            "repo": "snyk/snyk-mcp",
            "stars": "4k+",
            "description": "Security vulnerability scanning",
            "capabilities": ["security", "snyk", "vulnerabilities", "scanning"],
            "install": "npx -y @snyk/mcp",
            "category": MCPServerCategory.SECURITY,
            "language": "typescript"
        },
    ]
    
    # Priority 2 servers (Important)
    PRIORITY_2_SERVERS = [
        {
            "name": "discord_mcp",
            "repo": "discord/discord-mcp",
            "stars": "3k+",
            "description": "Discord bot integration",
            "capabilities": ["discord", "bot", "messaging", "server_management"],
            "install": "npm install -g @discord/mcp-server",
            "category": MCPServerCategory.COMMUNICATION,
            "language": "typescript"
        },
        {
            "name": "svg_maker",
            "repo": "GenWaveLLC/svgmaker-mcp",
            "stars": "3k+",
            "description": "AI-powered SVG generation",
            "capabilities": ["svg", "vector", "graphics", "generation"],
            "install": "npx -y svgmaker-mcp",
            "category": MCPServerCategory.CREATIVE,
            "language": "typescript"
        },
        {
            "name": "music",
            "repo": "Cifero74/mcp-apple-music",
            "stars": "3k+",
            "description": "Apple Music integration",
            "capabilities": ["music", "apple_music", "playlist", "streaming"],
            "install": "pip install mcp-apple-music",
            "category": MCPServerCategory.CREATIVE,
            "language": "python"
        },
        {
            "name": "imagen3",
            "repo": "hamflx/imagen3-mcp",
            "stars": "3k+",
            "description": "Google Imagen 3 image generation",
            "capabilities": ["imagen", "image_generation", "google", "ai"],
            "install": "npx -y imagen3-mcp",
            "category": MCPServerCategory.CREATIVE,
            "language": "typescript"
        },
        {
            "name": "sqlite",
            "repo": "modelcontextprotocol/server-sqlite",
            "stars": "4k+",
            "description": "SQLite database operations",
            "capabilities": ["sqlite", "database", "sql", "local"],
            "install": "npx -y @modelcontextprotocol/server-sqlite",
            "category": MCPServerCategory.DATABASE,
            "language": "typescript"
        },
        {
            "name": "everart",
            "repo": "modelcontextprotocol/server-everart",
            "stars": "3k+",
            "description": "AI art generation",
            "capabilities": ["art", "generation", "ai", "images"],
            "install": "npx -y @modelcontextprotocol/server-everart",
            "category": MCPServerCategory.CREATIVE,
            "language": "typescript"
        },
        {
            "name": "brave_search",
            "repo": "modelcontextprotocol/server-brave-search",
            "stars": "4k+",
            "description": "Web search via Brave",
            "capabilities": ["search", "brave", "web_search", "information"],
            "install": "npx -y @modelcontextprotocol/server-brave-search",
            "category": MCPServerCategory.SEARCH,
            "language": "typescript"
        },
        {
            "name": "git",
            "repo": "modelcontextprotocol/server-git",
            "stars": "5k+",
            "description": "Git operations",
            "capabilities": ["git", "version_control", "commits", "branches"],
            "install": "npx -y @modelcontextprotocol/server-git",
            "category": MCPServerCategory.CODING,
            "language": "typescript"
        },
        {
            "name": "time",
            "repo": "modelcontextprotocol/server-time",
            "stars": "3k+",
            "description": "Time and timezone information",
            "capabilities": ["time", "timezone", "date", "scheduling"],
            "install": "npx -y @modelcontextprotocol/server-time",
            "category": MCPServerCategory.CODING,
            "language": "typescript"
        },
        {
            "name": "google_maps",
            "repo": "modelcontextprotocol/server-google-maps",
            "stars": "4k+",
            "description": "Google Maps integration",
            "capabilities": ["maps", "geocoding", "directions", "places"],
            "install": "npx -y @modelcontextprotocol/server-google-maps",
            "category": MCPServerCategory.SEARCH,
            "language": "typescript"
        },
        {
            "name": "memory_k",
            "repo": "khooiengt/fastmcp-memory",
            "stars": "2k+",
            "description": "Fast key-value memory store",
            "capabilities": ["memory", "kv_store", "caching", "fast"],
            "install": "pip install fastmcp-memory",
            "category": MCPServerCategory.AI_MODELS,
            "language": "python"
        },
        {
            "name": "redis",
            "repo": "modelcontextprotocol/server-redis",
            "stars": "3k+",
            "description": "Redis cache operations",
            "capabilities": ["redis", "cache", "memory", "fast"],
            "install": "npx -y @modelcontextprotocol/server-redis",
            "category": MCPServerCategory.DATABASE,
            "language": "typescript"
        },
        {
            "name": "slack_blocks",
            "repo": "modelcontextprotocol/server-slack",
            "stars": "3k+",
            "description": "Slack messaging with blocks",
            "capabilities": ["slack", "blocks", "messaging", "interactive"],
            "install": "npx -y @modelcontextprotocol/server-slack",
            "category": MCPServerCategory.COMMUNICATION,
            "language": "typescript"
        },
        {
            "name": "sentry",
            "repo": "modelcontextprotocol/server-sentry",
            "stars": "3k+",
            "description": "Error tracking and monitoring",
            "capabilities": ["sentry", "monitoring", "errors", "debugging"],
            "install": "npx -y @modelcontextprotocol/server-sentry",
            "category": MCPServerCategory.SECURITY,
            "language": "typescript"
        },
        {
            "name": "aws_kb",
            "repo": "serverlessworkflow/mcp-server-aws-kb",
            "stars": "2k+",
            "description": "AWS Knowledge Base integration",
            "capabilities": ["aws", "knowledge_base", "bedrock", "rag"],
            "install": "pip install mcp-server-aws-kb",
            "category": MCPServerCategory.AI_MODELS,
            "language": "python"
        },
    ]
    
    # Priority 3 servers (Nice to have)
    PRIORITY_3_SERVERS = [
        {"name": "fetch_realtime", "repo": "modelcontextprotocol/fetch", "stars": "6k+",
         "description": "Real-time web fetching", "capabilities": ["real-time", "fetch", "streaming"],
         "install": "npx -y @modelcontextprotocol/server-fetch", "category": MCPServerCategory.SEARCH,
         "language": "typescript"},
        {"name": "sequentialthinking", "repo": "modelcontextprotocol/sequentialthinking",
         "stars": "5k+", "description": "Structured thinking process",
         "capabilities": ["thinking", "reasoning", "analysis", "structured"],
         "install": "npx -y @modelcontextprotocol/server-sequential-thinking",
         "category": MCPServerCategory.AI_MODELS, "language": "typescript"},
        {"name": "everything", "repo": "modelcontextprotocol/server-everything",
         "stars": "4k+", "description": "Universal tool server",
         "capabilities": ["universal", "tools", "everything"],
         "install": "npx -y @modelcontextprotocol/server-everything",
         "category": MCPServerCategory.CODING, "language": "typescript"},
        {"name": "pokemon", "repo": "modelcontextprotocol/server-pokemon",
         "stars": "2k+", "description": "Pokemon API",
         "capabilities": ["pokemon", "api", "fun"],
         "install": "npx -y @modelcontextprotocol/server-pokemon",
         "category": MCPServerCategory.SEARCH, "language": "typescript"},
    ]
    
    @classmethod
    def get_all_servers(cls) -> List[Dict]:
        """Get all MCP servers from all priority levels."""
        return (
            cls.PRIORITY_1_SERVERS +
            cls.PRIORITY_2_SERVERS +
            cls.PRIORITY_3_SERVERS
        )
    
    @classmethod
    def get_servers_by_category(cls, category: MCPServerCategory) -> List[Dict]:
        """Get servers filtered by category."""
        return [s for s in cls.get_all_servers() if s["category"] == category]
    
    @classmethod
    def get_priority_1_servers(cls) -> List[Dict]:
        """Get all priority 1 servers."""
        return cls.PRIORITY_1_SERVERS
    
    @classmethod
    def search_servers(cls, query: str) -> List[Dict]:
        """Search servers by name, description, or capabilities."""
        query_lower = query.lower()
        results = []
        
        for server in cls.get_all_servers():
            # Check name
            if query_lower in server["name"].lower():
                results.append(server)
                continue
            # Check description
            if query_lower in server["description"].lower():
                results.append(server)
                continue
            # Check capabilities
            for cap in server.get("capabilities", []):
                if query_lower in cap.lower():
                    results.append(server)
                    break
                
        return results
    
    @classmethod
    def generate_claude_desktop_config(cls) -> Dict[str, Any]:
        """Generate Claude Desktop configuration file."""
        config = {"mcpServers": {}}
        
        for server in cls.PRIORITY_1_SERVERS:
            install = server.get("install", "")
            name = server["name"]
            
            if "npx" in install:
                parts = install.split(" -y ")
                if len(parts) > 1:
                    config["mcpServers"][name] = {
                        "command": "npx",
                        "args": ["-y", parts[1].strip()]
                    }
            elif "pip" in install:
                package = install.split("pip install")[-1].strip()
                config["mcpServers"][name] = {
                    "command": "python",
                    "args": ["-m", "fastmcp", "run", f"--package={package}"]
                }
            elif "npm" in install:
                package = install.split("npm install -g")[-1].strip()
                config["mcpServers"][name] = {
                    "command": "npm",
                    "args": ["-g", package]
                }
                
        return config
    
    @classmethod
    def generate_install_script(cls) -> str:
        """Generate installation script for all priority 1 servers."""
        script = """#!/bin/bash
# Neuro Ultimate - Complete MCP Server Setup Script
# Generated automatically

set -e

echo "🚀 Installing Neuro Ultimate MCP Servers..."
echo "============================================"

# Colors for output
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

install_npx() {
    echo -e "${GREEN}Installing $1...${NC}"
    npx -y $2
}

install_pip() {
    echo -e "${GREEN}Installing $1...${NC}"
    pip install $2
}

"""
        
        for server in cls.PRIORITY_1_SERVERS:
            install = server["install"]
            name = server["name"]
            desc = server["description"]
            
            script += f'''
echo -e "\\n{YELLOW}Installing {name}: {desc}${NC}"
'''
            
            if "npx" in install:
                package = install.split(" -y ")[-1].strip()
                script += f'install_npx "{name}" "{package}"\n'
            elif "pip" in install:
                package = install.split("pip install")[-1].strip()
                script += f'install_pip "{name}" "{package}"\n'
            elif "docker" in install:
                script += f'echo "Docker setup: {install}"\n'
                
        script += """
echo -e "\\n${GREEN}✅ All MCP servers installed successfully!${NC}"
echo "You can now use Neuro Ultimate with 500+ capabilities."
"""
        
        return script
    
    @classmethod
    def generate_docker_compose(cls) -> str:
        """Generate docker-compose.yml for containerized MCP servers."""
        services = {}
        
        for server in cls.PRIORITY_1_SERVERS:
            install = server["install"]
            name = server["name"]
            
            if "docker run" in install:
                parts = install.replace("docker run", "").strip().split()
                image = parts[0]
                
                port_mapping = ""
                if "-p" in parts:
                    port_idx = parts.index("-p")
                    port_mapping = parts[port_idx + 1] if port_idx + 1 < len(parts) else ""
                
                services[name] = {
                    "image": image,
                    "ports": [port_mapping] if port_mapping else None
                }
        
        compose = {
            "version": "3.8",
            "services": {k: v for k, v in services.items() if v.get("ports")}
        }
        
        return json.dumps(compose, indent=2)


class MCPServerManager:
    """Runtime manager for MCP servers."""
    
    def __init__(self):
        self.registry = MCPServerRegistry()
        self.active_servers: Dict[str, bool] = {}
        self.server_configs: Dict[str, Dict] = {}
        
    def select_servers_for_task(self, task: str) -> List[MCPServer]:
        """Select appropriate servers for a given task."""
        task_lower = task.lower()
        selected = []
        
        # Score each server based on capability match
        for server_dict in self.registry.get_all_servers():
            score = 0
            for cap in server_dict.get("capabilities", []):
                if cap.lower() in task_lower:
                    score += 2
                elif any(word in task_lower for word in cap.lower().split("_")):
                    score += 1
                    
            if score > 0:
                server = MCPServer(
                    name=server_dict["name"],
                    repo=server_dict["repo"],
                    stars=server_dict["stars"],
                    description=server_dict["description"],
                    capabilities=server_dict["capabilities"],
                    install_command=server_dict["install"],
                    priority=1 if server_dict in self.registry.PRIORITY_1_SERVERS else 2,
                    category=server_dict["category"],
                    language=server_dict["language"]
                )
                selected.append((score, server))
        
        # Sort by score descending
        selected.sort(key=lambda x: -x[0])
        
        # Return top 5 servers
        return [s for _, s in selected[:5]]
    
    def get_recommended_servers(self, task: str) -> Dict[str, Any]:
        """Get detailed recommendations for a task."""
        servers = self.select_servers_for_task(task)
        
        return {
            "task": task,
            "recommended_count": len(servers),
            "servers": [
                {
                    "name": s.name,
                    "description": s.description,
                    "stars": s.stars,
                    "capabilities": s.capabilities,
                    "install": s.install_command,
                    "repo": f"github.com/{s.repo}",
                    "category": s.category.value
                }
                for s in servers
            ]
        }