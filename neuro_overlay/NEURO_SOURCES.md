# Neuro complementary repositories

This repo uses OpenHands as the base runtime and integrates complementary projects through adapters, dependency files, and scripts.

## Base runtime

- OpenHands/OpenHands: sandbox, tools, terminal, file editing, browser tools, UI, GitHub workflow.

## Complementary projects

- browser-use/browser-use: autonomous browser automation adapter.
- langchain-ai/langgraph: multi-agent orchestration graph layer.
- BerriAI/litellm: provider routing gateway and OpenAI-compatible proxy.
- microsoft/playwright: deterministic browser automation and tests.

## Integration policy

Do not vendor all third-party repositories into the runtime tree by default. Keep OpenHands materialized as the base and integrate the others through package dependencies, thin adapters, and optional reference clones under `.external/`.
