"""
Neuro MCP Integration Skill (swarmclaw)
Model Context Protocol integration for enhanced AI capabilities
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class MCPProvider(Enum):
    """Supported MCP providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    custom = "custom"

@dataclass
class MCPConfig:
    """MCP server configuration"""
    provider: MCPProvider
    endpoint: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096

class MCPSkill:
    """
    MCP Integration for Neuro - Provides Model Context Protocol capabilities
    Enables connection to various LLM providers with unified interface
    """
    
    NAME = "mcp_integration"
    DESCRIPTION = "Model Context Protocol integration for connecting to external AI models and services"
    TRIGGERS = ["mcp", "model context", "provider", "ollama", "lm studio", "api key"]
    
    # Default MCP endpoints
    DEFAULT_ENDPOINTS = {
        MCPProvider.OLLAMA: "http://localhost:11434",
        MCPProvider.LM_STUDIO: "http://localhost:1234",
        MCPProvider.OPENAI: "https://api.openai.com/v1",
        MCPProvider.ANTHROPIC: "https://api.anthropic.com/v1",
    }
    
    @classmethod
    def create_config(
        cls,
        provider: str = "ollama",
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "llama2",
        **kwargs
    ) -> MCPConfig:
        """Create MCP configuration"""
        provider_enum = MCPProvider(provider) if provider in [p.value for p in MCPProvider] else MCPProvider.custom
        
        return MCPConfig(
            provider=provider_enum,
            endpoint=endpoint or cls.DEFAULT_ENDPOINTS.get(provider_enum, ""),
            api_key=api_key,
            model=model,
            **{k: v for k, v in kwargs.items() if k in ["temperature", "max_tokens"]}
        )
    
    @classmethod
    def format_context(cls, context: Dict[str, Any]) -> str:
        """Format context for MCP"""
        formatted = []
        if "task" in context:
            formatted.append(f"Task: {context['task']}")
        if "code" in context:
            formatted.append(f"Code:\n{context['code']}")
        if "errors" in context:
            formatted.append(f"Errors: {context['errors']}")
        return "\n\n".join(formatted)
    
    @classmethod
    def generate_mcp_prompt(cls, task: str, context: Dict[str, Any] = None) -> str:
        """Generate MCP-compatible prompt"""
        base_prompt = f"Task: {task}\n"
        if context:
            base_prompt += f"Context: {cls.format_context(context)}\n"
        return base_prompt
    
    @classmethod
    def get_capabilities(cls) -> List[str]:
        """Return MCP capabilities"""
        return [
            "Multi-provider LLM support",
            "Unified API interface",
            "Context enrichment",
            "Tool use integration",
            "Streaming responses",
            "Custom model configuration"
        ]
    
    @classmethod
    def invoke(cls, task: str, config: Optional[MCPConfig] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main entry point for MCP skill invocation
        Returns configuration and prompt for external MCP processing
        """
        return {
            "skill": cls.NAME,
            "provider": config.provider.value if config else "ollama",
            "endpoint": config.endpoint if config else cls.DEFAULT_ENDPOINTS.get(MCPProvider.OLLAMA),
            "model": config.model if config else "llama2",
            "prompt": cls.generate_mcp_prompt(task, context),
            "capabilities": cls.get_capabilities(),
            "configurable": True
        }

# Convenience function
def mcp_invoke(task: str, **kwargs) -> Dict[str, Any]:
    """Invoke MCP skill"""
    config = MCPSkill.create_config(**kwargs) if kwargs else None
    return MCPSkill.invoke(task, config)
