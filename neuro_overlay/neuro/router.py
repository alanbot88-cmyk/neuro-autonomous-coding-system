from __future__ import annotations

from typing import Any, Dict, List

ROLE_MODEL_ALIASES: dict[str, list[str]] = {
    "planner": ["neuro-planner", "neuro-executor"],
    "executor": ["neuro-executor", "neuro-coder", "neuro-planner"],
    "debugger": ["neuro-debugger", "neuro-planner"],
    "coder": ["neuro-coder", "neuro-executor"],
    "observer": ["neuro-observer", "neuro-condenser"],
    "condenser": ["neuro-condenser", "neuro-observer"],
}


def complete(role: str, messages: List[Dict[str, str]], **kwargs: Any) -> str:
    raise RuntimeError(
        "Neuro router is configured through the LiteLLM proxy aliases in config/litellm.config.yaml. "
        "Use OpenHands with model litellm_proxy/neuro-executor, or replace this skeleton with a direct LiteLLM client inside a private environment."
    )


def available_roles() -> dict[str, list[str]]:
    return ROLE_MODEL_ALIASES
