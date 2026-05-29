"""
Scenario Router - Intelligent task routing based on scenario detection
Routes tasks to specialized handlers with optimized approaches
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# SCENARIO DEFINITIONS
# =============================================================================

class ScenarioType(Enum):
    """Enumeration of supported scenario types."""
    BUG_FIX = "bug_fix"
    NEW_FEATURE = "new_feature"
    REFACTOR = "refactor"
    WEB_APP = "web_app"
    API_BUILD = "api_build"
    DATA_PIPELINE = "data_pipeline"
    CODE_REVIEW = "code_review"
    RESEARCH_TASK = "research_task"
    LONG_HORIZON = "long_horizon"
    ENTERPRISE_APP = "enterprise_app"
    MOBILE_APP = "mobile_app"
    PRESENTATION = "presentation"


@dataclass
class ScenarioHandler:
    """Handler configuration for a specific scenario type."""
    scenario_type: ScenarioType
    approach: str
    tools: List[str]
    model_primary: str
    model_fallback: Optional[str] = None
    confidence_threshold: float = 0.6
    max_retries: int = 3
    special_instructions: List[str] = None
    
    def __post_init__(self):
        if self.special_instructions is None:
            self.special_instructions = []


# =============================================================================
# SCENARIO HANDLERS REGISTRY
# =============================================================================

SCENARIO_HANDLERS: Dict[ScenarioType, ScenarioHandler] = {
    ScenarioType.BUG_FIX: ScenarioHandler(
        scenario_type=ScenarioType.BUG_FIX,
        approach="diagnose-fix-verify",
        tools=["debugger", "shell_executor", "auto_fix_loop", "playwright_tester"],
        model_primary="groq/llama-3.3-70b-versatile",
        model_fallback="openrouter/qwen/qwen2.5-72b-instruct",
        confidence_threshold=0.7,
        max_retries=5,
        special_instructions=[
            "Use detailed error analysis first",
            "Test each fix before proceeding",
            "Keep track of what was tried"
        ]
    ),
    
    ScenarioType.NEW_FEATURE: ScenarioHandler(
        scenario_type=ScenarioType.NEW_FEATURE,
        approach="plan-implement-test",
        tools=["task_decomposer", "code_generator", "shell_executor", "playwright_tester"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="gemini/gemini-2.0-flash",
        confidence_threshold=0.6,
        max_retries=3,
        special_instructions=[
            "Create clear specification first",
            "Implement incrementally",
            "Test each component"
        ]
    ),
    
    ScenarioType.REFACTOR: ScenarioHandler(
        scenario_type=ScenarioType.REFACTOR,
        approach="analyze-plan-execute-verify",
        tools=["code_analysis", "task_decomposer", "shell_executor", "git_operations"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="groq/llama-3.3-70b-versatile",
        confidence_threshold=0.65,
        max_retries=3,
        special_instructions=[
            "Preserve existing functionality",
            "Run full test suite after changes",
            "Review code quality improvements"
        ]
    ),
    
    ScenarioType.WEB_APP: ScenarioHandler(
        scenario_type=ScenarioType.WEB_APP,
        approach="design-backend-frontend-integrate-test",
        tools=["task_decomposer", "code_generator", "component_driven", "playwright_tester", "browser_automation"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="gemini/gemini-2.0-flash",
        confidence_threshold=0.7,
        max_retries=3,
        special_instructions=[
            "Use component-driven development",
            "Responsive design by default",
            "Test on multiple browsers"
        ]
    ),
    
    ScenarioType.API_BUILD: ScenarioHandler(
        scenario_type=ScenarioType.API_BUILD,
        approach="design-schema-implement-document",
        tools=["task_decomposer", "code_generator", "shell_executor", "api_testing"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="groq/llama-3.3-70b-versatile",
        confidence_threshold=0.7,
        max_retries=3,
        special_instructions=[
            "Design API schema first",
            "Document all endpoints",
            "Include error handling"
        ]
    ),
    
    ScenarioType.DATA_PIPELINE: ScenarioHandler(
        scenario_type=ScenarioType.DATA_PIPELINE,
        approach="analyze-design-implement-validate",
        tools=["task_decomposer", "code_generator", "shell_executor", "data_validation"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="gemini/gemini-2.0-flash",
        confidence_threshold=0.65,
        max_retries=2,
        special_instructions=[
            "Handle data quality issues",
            "Include error handling",
            "Document transformation logic"
        ]
    ),
    
    ScenarioType.CODE_REVIEW: ScenarioHandler(
        scenario_type=ScenarioType.CODE_REVIEW,
        approach="analyze-identify-suggest",
        tools=["code_analysis", "git_operations", "shell_executor"],
        model_primary="groq/llama-3.3-70b-versatile",
        model_fallback="openrouter/qwen/qwen2.5-72b-instruct",
        confidence_threshold=0.8,
        max_retries=2,
        special_instructions=[
            "Review for security issues first",
            "Check code quality patterns",
            "Suggest concrete improvements"
        ]
    ),
    
    ScenarioType.RESEARCH_TASK: ScenarioHandler(
        scenario_type=ScenarioType.RESEARCH_TASK,
        approach="gather-analyze-summarize",
        tools=["deep_research", "web_browser", "document_generator"],
        model_primary="gemini/gemini-2.0-flash",
        model_fallback="openrouter/deepseek/deepseek-chat-v3-0324",
        confidence_threshold=0.6,
        max_retries=2,
        special_instructions=[
            "Focus on accuracy over speed",
            "Cite sources for claims",
            "Provide actionable insights"
        ]
    ),
    
    ScenarioType.LONG_HORIZON: ScenarioHandler(
        scenario_type=ScenarioType.LONG_HORIZON,
        approach="milestone-track-iterate",
        tools=["task_decomposer", "progress_tracker", "multi_agent", "verification_loop"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="gemini/gemini-2.0-flash",
        confidence_threshold=0.5,
        max_retries=3,
        special_instructions=[
            "Break into achievable milestones",
            "Track progress frequently",
            "Replan when needed"
        ]
    ),
    
    ScenarioType.ENTERPRISE_APP: ScenarioHandler(
        scenario_type=ScenarioType.ENTERPRISE_APP,
        approach="architecture-design-implement-test-deploy",
        tools=["task_decomposer", "component_driven", "multi_agent", "playwright_tester", "shell_executor"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="gemini/gemini-2.0-flash",
        confidence_threshold=0.6,
        max_retries=3,
        special_instructions=[
            "Use enterprise architecture patterns",
            "Security by design",
            "Comprehensive testing",
            "Documentation required"
        ]
    ),
    
    ScenarioType.MOBILE_APP: ScenarioHandler(
        scenario_type=ScenarioType.MOBILE_APP,
        approach="design-implement-test-package",
        tools=["task_decomposer", "code_generator", "shell_executor", "mobile_tester"],
        model_primary="openrouter/deepseek/deepseek-chat-v3-0324",
        model_fallback="gemini/gemini-2.0-flash",
        confidence_threshold=0.6,
        max_retries=3,
        special_instructions=[
            "Platform-specific best practices",
            "Responsive mobile design",
            "Test on multiple devices"
        ]
    ),
    
    ScenarioType.PRESENTATION: ScenarioHandler(
        scenario_type=ScenarioType.PRESENTATION,
        approach="outline-design-build-refine",
        tools=["slide_builder", "document_generator", "component_driven"],
        model_primary="gemini/gemini-2.0-flash",
        model_fallback="openrouter/deepseek/deepseek-chat-v3-0324",
        confidence_threshold=0.8,
        max_retries=2,
        special_instructions=[
            "Professional visual design",
            "Clear narrative flow",
            "Appropriate for audience"
        ]
    ),
}


# =============================================================================
# KEYWORD PATTERNS FOR SCENARIO DETECTION
# =============================================================================

SCENARIO_KEYWORDS: Dict[ScenarioType, Tuple[List[str], List[str]]] = {
    ScenarioType.BUG_FIX: (
        ["bug", "fix", "error", "crash", "exception", "issue", "broken", "not working", "failed"],
        ["SyntaxError", "ImportError", "TypeError", "AttributeError", "null", "undefined"]
    ),
    ScenarioType.NEW_FEATURE: (
        ["add", "new feature", "implement", "create", "build", "develop"],
        ["feature request", "enhancement"]
    ),
    ScenarioType.REFACTOR: (
        ["refactor", "restructure", "clean up", "improve", "optimize", "reorganize"],
        ["technical debt", "code quality"]
    ),
    ScenarioType.WEB_APP: (
        ["web app", "website", "landing page", "frontend", "react", "vue", "angular", "html"],
        ["ui", "dashboard", "portal"]
    ),
    ScenarioType.API_BUILD: (
        ["api", "rest", "graphql", "endpoint", "backend", "server", "microservice"],
        ["crud", "webhook"]
    ),
    ScenarioType.DATA_PIPELINE: (
        ["pipeline", "etl", "data processing", "transform", "stream", "batch"],
        ["data flow", "ingestion"]
    ),
    ScenarioType.CODE_REVIEW: (
        ["review", "audit", "check", "analyze code", "review pr"],
        ["pull request", "merge"]
    ),
    ScenarioType.RESEARCH_TASK: (
        ["research", "investigate", "find out", "explore", "study", "analyze"],
        ["compare", "benchmark"]
    ),
    ScenarioType.LONG_HORIZON: (
        ["large", "big", "complex", "enterprise", "saas", "system"],
        ["multi-module", "full-stack"]
    ),
    ScenarioType.ENTERPRISE_APP: (
        ["enterprise", "saas", "crm", "erp", "admin", "dashboard", "management system"],
        ["multi-tenant", "scalable"]
    ),
    ScenarioType.MOBILE_APP: (
        ["mobile", "ios", "android", "app", "phone", "tablet"],
        ["react native", "flutter"]
    ),
    ScenarioType.PRESENTATION: (
        ["presentation", "slides", "deck", "pitch", "talk", "demo"],
        ["keynote", "powerpoint"]
    ),
}


# =============================================================================
# SCENARIO ROUTER
# =============================================================================

class ScenarioRouter:
    """
    Routes tasks to specialized handlers based on scenario detection.
    
    Uses keyword matching and semantic classification to identify
    the appropriate scenario type and handler for a given task.
    
    Usage:
        router = ScenarioRouter()
        scenario = router.detect_scenario("Fix the login bug")
        handler = router.get_handler(scenario)
        config = router.route("Fix the login bug")
    """
    
    def __init__(self, fallback_scenario: ScenarioType = ScenarioType.NEW_FEATURE):
        self.fallback_scenario = fallback_scenario
        self._detection_cache: Dict[str, ScenarioType] = {}
    
    def detect_scenario(self, task: str) -> Tuple[ScenarioType, float]:
        """
        Detect the scenario type for a given task.
        
        Args:
            task: The task description to analyze
            
        Returns:
            Tuple of (detected scenario type, confidence score)
        """
        task_lower = task.lower()
        
        # Check cache first
        cache_key = task_lower[:100]  # Use first 100 chars as key
        if cache_key in self._detection_cache:
            return self._detection_cache[cache_key], 0.9
        
        # Keyword-based detection
        scores: Dict[ScenarioType, float] = {}
        
        for scenario_type, (primary_kw, secondary_kw) in SCENARIO_KEYWORDS.items():
            score = 0.0
            
            # Primary keywords (higher weight)
            for kw in primary_kw:
                if kw in task_lower:
                    score += 0.3
                    # Bonus for exact match
                    if kw == task_lower:
                        score += 0.2
            
            # Secondary keywords (lower weight)
            for kw in secondary_kw:
                if kw in task_lower:
                    score += 0.1
            
            if score > 0:
                scores[scenario_type] = min(score, 1.0)
        
        # Semantic classification using common patterns
        semantic_score = self._semantic_classification(task_lower)
        for scenario_type, score in semantic_score.items():
            scores[scenario_type] = scores.get(scenario_type, 0) + score
        
        # Find best match
        if scores:
            best_scenario = max(scores, key=scores.get)
            confidence = scores[best_scenario]
            
            # Check threshold
            handler = SCENARIO_HANDLERS.get(best_scenario)
            if handler and confidence >= handler.confidence_threshold:
                self._detection_cache[cache_key] = best_scenario
                return best_scenario, confidence
        
        # Fallback
        return self.fallback_scenario, 0.3
    
    def _semantic_classification(self, task_lower: str) -> Dict[ScenarioType, float]:
        """
        Additional semantic classification beyond keywords.
        
        Uses patterns and contextual clues to improve detection.
        """
        scores: Dict[ScenarioType, float] = {}
        
        # Pattern: "fix X until it works" → BUG_FIX
        fix_patterns = [
            r"fix.*until.*works",
            r"debug.*crash",
            r"error.*in.*line",
            r"exception.*occurring"
        ]
        for pattern in fix_patterns:
            if re.search(pattern, task_lower):
                scores[ScenarioType.BUG_FIX] = scores.get(ScenarioType.BUG_FIX, 0) + 0.4
        
        # Pattern: "build/create/implement X app" → WEB_APP or ENTERPRISE_APP
        build_patterns = [
            r"build.*app",
            r"create.*app",
            r"implement.*app"
        ]
        for pattern in build_patterns:
            if re.search(pattern, task_lower):
                if "enterprise" in task_lower or "saas" in task_lower:
                    scores[ScenarioType.ENTERPRISE_APP] = scores.get(ScenarioType.ENTERPRISE_APP, 0) + 0.5
                else:
                    scores[ScenarioType.WEB_APP] = scores.get(ScenarioType.WEB_APP, 0) + 0.4
        
        # Pattern: "deploy to X" → DEPLOY (may need special handling)
        deploy_patterns = [
            r"deploy.*vercel",
            r"deploy.*heroku",
            r"deploy.*aws",
            r"push.*production"
        ]
        for pattern in deploy_patterns:
            if re.search(pattern, task_lower):
                scores[ScenarioType.LONG_HORIZON] = scores.get(ScenarioType.LONG_HORIZON, 0) + 0.3
        
        # Pattern: "make slides" → PRESENTATION
        if "slide" in task_lower or "presentation" in task_lower:
            scores[ScenarioType.PRESENTATION] = 0.8
        
        # Pattern: "multi-agent" or "parallel" → LONG_HORIZON
        if "multi-agent" in task_lower or "parallel" in task_lower:
            scores[ScenarioType.LONG_HORIZON] = scores.get(ScenarioType.LONG_HORIZON, 0) + 0.3
        
        return scores
    
    def get_handler(self, scenario: ScenarioType) -> ScenarioHandler:
        """
        Get the handler configuration for a scenario type.
        
        Args:
            scenario: The scenario type to get handler for
            
        Returns:
            ScenarioHandler configuration
        """
        return SCENARIO_HANDLERS.get(
            scenario,
            SCENARIO_HANDLERS[self.fallback_scenario]
        )
    
    def route(self, task: str) -> Dict[str, Any]:
        """
        Route a task to the appropriate handler.
        
        Args:
            task: The task description
            
        Returns:
            Dictionary with routing configuration including:
            - scenario: detected scenario type
            - confidence: detection confidence
            - handler: handler configuration
            - approach: recommended approach
            - tools: recommended tools
            - models: recommended models with fallback
            - special_instructions: scenario-specific instructions
        """
        scenario, confidence = self.detect_scenario(task)
        handler = self.get_handler(scenario)
        
        return {
            "scenario": scenario.value,
            "confidence": confidence,
            "approach": handler.approach,
            "tools": handler.tools,
            "model_primary": handler.model_primary,
            "model_fallback": handler.model_fallback,
            "max_retries": handler.max_retries,
            "special_instructions": handler.special_instructions,
        }
    
    def force_scenario(self, task: str, scenario: ScenarioType) -> Dict[str, Any]:
        """
        Force a specific scenario handler for a task.
        
        Useful when automatic detection is incorrect or when
        user explicitly specifies scenario type.
        
        Args:
            task: The task description
            scenario: The scenario type to force
            
        Returns:
            Dictionary with routing configuration
        """
        handler = self.get_handler(scenario)
        
        return {
            "scenario": scenario.value,
            "confidence": 1.0,  # Forced, so high confidence
            "approach": handler.approach,
            "tools": handler.tools,
            "model_primary": handler.model_primary,
            "model_fallback": handler.model_fallback,
            "max_retries": handler.max_retries,
            "special_instructions": handler.special_instructions,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def detect_task_scenario(task: str) -> Tuple[ScenarioType, float]:
    """Quick function to detect scenario."""
    router = ScenarioRouter()
    return router.detect_scenario(task)


def get_routing_config(task: str) -> Dict[str, Any]:
    """Quick function to get full routing config."""
    router = ScenarioRouter()
    return router.route(task)


def force_scenario_handler(task: str, scenario_name: str) -> Dict[str, Any]:
    """
    Force a specific scenario handler by name.
    
    Args:
        task: The task description
        scenario_name: String name of scenario (e.g., "bug_fix", "web_app")
    """
    router = ScenarioRouter()
    
    # Convert string to enum
    try:
        scenario = ScenarioType(scenario_name)
    except ValueError:
        raise ValueError(f"Unknown scenario: {scenario_name}. Valid: {[s.value for s in ScenarioType]}")
    
    return router.force_scenario(task, scenario)


# =============================================================================
# SKILL.md CONTENT
# =============================================================================

SKILL_MD = """
---
name: scenario-router
description: Intelligent task routing based on scenario detection
triggers:
  - scenario
  - route
  - detect
  - specialize
---

# Scenario Router

Routes tasks to specialized handlers based on detected scenario type.

## Supported Scenarios

| Scenario | Approach | Best For |
|----------|----------|----------|
| bug_fix | diagnose-fix-verify | Fixing errors and crashes |
| new_feature | plan-implement-test | Adding new functionality |
| refactor | analyze-plan-execute-verify | Code improvements |
| web_app | design-backend-frontend-integrate-test | Web applications |
| api_build | design-schema-implement-document | REST/GraphQL APIs |
| data_pipeline | analyze-design-implement-validate | ETL and data processing |
| code_review | analyze-identify-suggest | Code quality audits |
| research_task | gather-analyze-summarize | Investigation and research |
| long_horizon | milestone-track-iterate | Large complex projects |
| enterprise_app | architecture-design-implement-test-deploy | SaaS/CRM/ERP systems |
| mobile_app | design-implement-test-package | iOS/Android apps |
| presentation | outline-design-build-refine | Slides and presentations |

## Usage

```python
from neuro.router.scenario_router import ScenarioRouter, detect_task_scenario

# Auto-detect scenario
router = ScenarioRouter()
scenario, confidence = router.detect_scenario("Fix the login bug")

# Get full routing config
config = router.route("Build a web app")

# Force specific scenario
config = router.force_scenario("Fix bug", ScenarioType.BUG_FIX)
```

## Configuration

Each handler specifies:
- approach: Recommended workflow
- tools: Recommended skill modules
- models: Primary and fallback models
- confidence_threshold: Minimum confidence for detection
- special_instructions: Scenario-specific guidance
"""