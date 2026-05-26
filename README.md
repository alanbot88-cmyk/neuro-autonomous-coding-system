# Neuro Autonomous Coding System

This repository is a bootstrap repo for a full OpenHands-based autonomous coding stack.

It does not pretend to replace OpenHands. It materializes the real OpenHands source from `OpenHands/OpenHands`, then overlays Neuro routing, free-provider model config, LangGraph orchestration files, browser-use integration, and Docker Compose services.

## What will happen

A GitHub Action named **Materialize OpenHands + Neuro overlay** will:

1. clone the official OpenHands repository,
2. copy the full OpenHands source into this repo,
3. overlay the `neuro/`, `config/`, `scripts/`, `.env.example`, and `docker-compose.neuro.yml` files,
4. commit the resulting full codebase back to `main`,
5. write `.neuro-materialized` so it does not run repeatedly.

If the Action does not start automatically, open **Actions → Materialize OpenHands + Neuro overlay → Run workflow**.

## Why this is not just a 25 KB toy

The actual OpenHands source is pulled by the Action so your repo becomes a real OpenHands fork-style codebase without manually uploading thousands of files from iPhone.

## Core stack

- OpenHands: runtime, sandbox, web UI, tools, GitHub integration
- LiteLLM Proxy: one OpenAI-compatible gateway for Gemini/Groq/OpenRouter/Mistral/Cerebras/SambaNova/GitHub/Cloudflare
- LangGraph: optional multi-agent orchestration layer
- browser-use: optional browser automation layer
- ChromaDB + Redis: optional memory/state services

## First setup after materialization

Copy `.env.example` to `.env` and add only the keys you actually have. The router automatically skips providers with missing keys.

For OpenHands direct use:

```bash
cp .env.example .env
cp config/openhands.neuro.toml config.toml
```

For self-host Docker:

```bash
docker compose -f docker-compose.neuro.yml up --build
```

OpenHands UI: http://localhost:3000
LiteLLM Proxy: http://localhost:4000
ChromaDB: http://localhost:8000

## Important model reality rule

A model is considered safe for the free/no-card stack only when one of these is true:

1. the provider dashboard shows it under your free account,
2. OpenRouter model id ends with `:free`,
3. the official provider pricing page says free tier/no-card.

Do not hardcode paid Kimi/Claude/OpenAI models as defaults.

## iPhone usage path

1. Wait for the Action to materialize the repo.
2. Open OpenHands Cloud.
3. Connect this GitHub repo.
4. Launch it.
5. Give OpenHands this first instruction:

```text
Inspect this repository first. Do not rewrite it. Identify the OpenHands upstream source, the Neuro overlay, LiteLLM config, model router, browser-use integration, and LangGraph orchestrator. Then tell me the safest next implementation step.
```
