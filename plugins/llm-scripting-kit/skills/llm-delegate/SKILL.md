---
name: llm-delegate
description: Delegate a bounded prompt or review to an LLM endpoint or CLI harness configured through llm-scripting-kit. Use when the user asks another model, provider, Claude, Codex, or OpenCode to perform or critique work.
---

# LLM Delegate

Use the canonical `llm-scripting-kit` CLI installed in the shared runtime. It owns endpoint discovery, model resolution, credentials, harness dispatch, and error classification.

Runtime command:

- macOS/Linux: `~/.codex/.local-data/codex-plugins-kit/.venv/bin/llm-scripting-kit`
- Windows: `%USERPROFILE%\.codex\.local-data\codex-plugins-kit\.venv\Scripts\llm-scripting-kit.exe`

If it is missing, run this repository's `scripts/setup` (`scripts/setup.ps1` on Windows). Do not copy library code or recreate endpoint configuration in this plugin.

## Workflow

When the endpoint is named, use it. Otherwise inspect `endpoints` and select based on the user's goal and the configured entries. HTTP transports and the Claude, Codex, and OpenCode harnesses are all supported; do not ask for confirmation merely because the selected entry is a harness.

Use `models --endpoint NAME` when model choice is unresolved. Use `resolve` to inspect the final backend/model without executing it.

Send substantial prompts through stdin or UTF-8 files, not command arguments. Request JSON for machine consumption:

```text
llm-scripting-kit complete --endpoint NAME --model MODEL --format json < prompt.txt
```

The response text is at `response.text`. Preserve meaningful token/timing metadata when the user requests an audit or comparison.

Prefer native Codex background agents when the work is ordinary parallel Codex delegation and they satisfy the requested model/context needs. Use the Codex CLI harness when its configured model, effort, isolated process, or explicit user request makes it the appropriate backend.

On exit code 2, correct the endpoint/model/configuration request. Exit code 3 is a persistent halt such as authentication, credit, or rate limiting; report the classified cause. Exit code 1 is an execution failure. Never print credentials or place them in arguments.
