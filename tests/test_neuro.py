"""
Tests for neuro package imports and basic structure
"""

import pytest


class TestImports:
    """Test that all main packages can be imported."""

    def test_neuro_package_import(self):
        """Test that neuro package can be imported."""
        import neuro
        assert neuro is not None

    def test_neuro_models_import(self):
        """Test that models module can be imported."""
        from neuro import models
        assert models is not None

    def test_neuro_executor_import(self):
        """Test that executor module can be imported."""
        from neuro import executor
        assert executor is not None

    def test_neuro_router_import(self):
        """Test that router module can be imported."""
        from neuro import router
        assert router is not None

    def test_neuro_skills_import(self):
        """Test that skills module can be imported."""
        from neuro import skills
        assert skills is not None


class TestSkillRegistry:
    """Test skill registry functionality."""

    def test_skill_registry_exists(self):
        """Test that SKILL_REGISTRY is defined."""
        from neuro.skills import SKILL_REGISTRY
        assert isinstance(SKILL_REGISTRY, dict)
        assert len(SKILL_REGISTRY) > 0

    def test_core_skills_registered(self):
        """Test that core skills are registered."""
        from neuro.skills import SKILL_REGISTRY

        core_skills = [
            "automation",
            "mcp",
            "open_design_skills",
            "agent_memory",
            "browser_automation",
            "verification_loop",
            "python_patterns",
            "continuous_learning",
            "agent_shield",
            "swe_bench",
            "shell_executor",
            "auto_fix",
        ]

        for skill in core_skills:
            assert skill in SKILL_REGISTRY, f"Skill '{skill}' should be registered"

    def test_skill_manager_exists(self):
        """Test that SkillManager class exists."""
        from neuro.skills import SkillManager
        assert SkillManager is not None

    def test_invoke_skill_function_exists(self):
        """Test that invoke_skill function exists."""
        from neuro.skills import invoke_skill
        assert callable(invoke_skill)


class TestRouter:
    """Test router module."""

    def test_smart_router_exists(self):
        """Test that SmartRouter class exists."""
        from neuro.router.smart_router import SmartRouter
        assert SmartRouter is not None

    def test_fallback_handler_exists(self):
        """Test that FallbackHandler class exists."""
        from neuro.router.fallback import FallbackHandler
        assert FallbackHandler is not None


class TestReasoning:
    """Test reasoning module."""

    def test_chain_of_thought_exists(self):
        """Test that ChainOfThought class exists."""
        from neuro.reasoning.chain_of_thought import ChainOfThought
        assert ChainOfThought is not None

    def test_thinking_loop_exists(self):
        """Test that ThinkingLoop class exists."""
        from neuro.reasoning.thinking_loop import ThinkingLoop
        assert ThinkingLoop is not None

    def test_self_reflect_exists(self):
        """Test that SelfReflector class exists."""
        from neuro.reasoning.self_reflect import SelfReflector
        assert SelfReflector is not None


class TestValidation:
    """Test validation module."""

    def test_test_runner_exists(self):
        """Test that TestRunner class exists."""
        from neuro.validation.test_runner import TestRunner
        assert TestRunner is not None

    def test_patch_guard_exists(self):
        """Test that PatchGuard class exists."""
        from neuro.validation.patch_guard import PatchGuard
        assert PatchGuard is not None


class TestMemory:
    """Test memory module."""

    def test_task_store_exists(self):
        """Test that TaskStore class exists."""
        from neuro.memory.task_store import TaskStore
        assert TaskStore is not None


class TestExecutor:
    """Test executor module."""

    def test_neuro_agent_exists(self):
        """Test that NeuroAgent class exists."""
        from neuro.executor.agent_loop import NeuroAgent
        assert NeuroAgent is not None

    def test_create_agent_exists(self):
        """Test that create_agent function exists."""
        from neuro.executor.agent_loop import create_agent
        assert callable(create_agent)

    def test_run_goal_exists(self):
        """Test that run_goal function exists."""
        from neuro.executor.agent_loop import run_goal
        assert callable(run_goal)


class TestSWEBenchSkills:
    """Test SWE-bench related functionality."""

    def test_swe_bench_runner_exists(self):
        """Test that SWEBenchRunner class exists."""
        from neuro.skills.swe_bench_runner import SWEBenchRunner
        assert SWEBenchRunner is not None

    def test_swe_bench_prompts_exist(self):
        """Test that SWE-bench prompts exist."""
        from neuro.skills.swe_bench_prompts import SWE_BENCH_SYSTEM_PROMPT
        assert isinstance(SWE_BENCH_SYSTEM_PROMPT, str)
        assert len(SWE_BENCH_SYSTEM_PROMPT) > 0

    def test_agent_swarm_exists(self):
        """Test that AgentSwarmCoordinator exists."""
        from neuro.skills.agent_swarm import AgentSwarmCoordinator
        assert AgentSwarmCoordinator is not None


class TestModels:
    """Test models module."""

    def test_models_registry_exists(self):
        """Test that model registry exists."""
        from neuro.models import APPROVED_MODELS
        assert isinstance(APPROVED_MODELS, list)
        assert len(APPROVED_MODELS) > 0

    def test_model_structure(self):
        """Test that models have expected structure."""
        from neuro.models import APPROVED_MODELS

        # Models are strings in format "provider/model-name"
        for model in APPROVED_MODELS[:5]:  # Check first 5
            assert isinstance(model, str), "Model should be a string"
            assert "/" in model, f"Model '{model}' should have provider/model format"
            parts = model.split("/")
            assert len(parts) >= 2, f"Model '{model}' should have provider/model format"
