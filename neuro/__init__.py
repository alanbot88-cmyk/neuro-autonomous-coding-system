"""
Neuro Autonomous Agent - Enterprise App Builder System
Focus: Build, debug, test, and ship real enterprise applications

Architecture:
- Smart Router: Rotates across 50+ free API providers
- Product Intake: Parse vague goals into structured specs
- Architecture Planner: Generate app architecture automatically
- Safe File Operations: Controlled file editing with rollback
- Self-Healing: Auto-fix common errors
- Pipeline System: End-to-end enterprise app workflows
- QA System: Browser testing with Playwright
- Memory: Learn from engineering patterns

Modes:
- enterprise: Build full SaaS applications
- website: Build landing pages and marketing sites
- debug: Fix existing broken projects
- presentation: Build presentations
- api: Build API services
- refactor: Refactor existing code
- deploy: Deploy applications

Usage:
    from neuro import create_agent
    agent = create_agent(goal="Build a CRM for real estate agents")
    result = agent.run()

Pipeline Usage:
    from neuro.pipelines import run_pipeline
    result = run_pipeline(
        goal="Build a CRM for real estate agents",
        mode="enterprise",
        dry_run=True,
    )
"""

__version__ = "2.0.0"
__target__ = "Enterprise App Builder"

from neuro.executor.agent_loop import create_agent, run_goal, NeuroAgent, AgentResult, AgentConfig
from neuro.skills import SkillAutomation, get_skill_manager, auto_skills
from neuro.product import ProductSpec, RequirementParser, parse_goal
from neuro.architecture import ArchitecturePlan, AppArchitect, create_architecture
from neuro.workspace import SafeFileWriter, RepoMap, ChangeTracker, create_repo_map
from neuro.pipelines import run_pipeline, EnterpriseAppPipeline, DebugPipeline, PipelineContext
from neuro.healing import ErrorClassifier, auto_fix, DependencyResolver
from neuro.qa import RouteChecker, run_qa_checks
from neuro.stacks import STACKS, get_stack, select_stack_for_goal, StackProfile
from neuro.deploy import deploy_app, generate_deployment_files, list_platforms, DEPLOYERS
from neuro.deploy import DeploymentConfig

__all__ = [
    # Core
    "create_agent",
    "run_goal",
    "NeuroAgent",
    "AgentResult",
    "AgentConfig",
    "SkillAutomation",
    "get_skill_manager",
    "auto_skills",
    # Product/Intake
    "ProductSpec",
    "RequirementParser",
    "parse_goal",
    # Architecture
    "ArchitecturePlan",
    "AppArchitect",
    "create_architecture",
    # Workspace
    "SafeFileWriter",
    "RepoMap",
    "ChangeTracker",
    "create_repo_map",
    # Pipelines
    "run_pipeline",
    "EnterpriseAppPipeline",
    "DebugPipeline",
    "PipelineContext",
    # Healing
    "ErrorClassifier",
    "auto_fix",
    "DependencyResolver",
    # QA
    "RouteChecker",
    "run_qa_checks",
    # Stacks
    "STACKS",
    "get_stack",
    "select_stack_for_goal",
    "StackProfile",
    # Deploy
    "deploy_app",
    "generate_deployment_files",
    "list_platforms",
    "DEPLOYERS",
    "DeploymentConfig",
]
