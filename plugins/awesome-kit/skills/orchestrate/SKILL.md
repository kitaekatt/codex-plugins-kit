---
name: orchestrate
description: Orchestrate significant multi-part work through native Codex background agents and llm-scripting-kit endpoints or harnesses while preserving the main context for coordination and synthesis. Do not use for a small single-step task.
---

# Orchestrate

Act as the orchestrator. Keep this context focused on decomposition, routing,
decisions, and synthesis; delegate work whose raw inputs or output would consume
substantial context.

This is a Codex adapter for the durable procedure in the upstream Awesome Kit.
Do not invoke the upstream Claude orchestration renderer: its Agent types,
model menu, and bootstrap runtime are Claude-specific.

## Available execution paths

Prefer native Codex background agents when they can do the work efficiently.
They provide lifecycle reporting, follow-ups, and parallel execution without
starting another Codex CLI process. Launch independent units concurrently and
give each writing unit exclusive file ownership or an isolated worktree.

All configured `llm-scripting-kit` transports and harnesses are also first-class
routing targets. Discover them at orchestration time; never remember a model
list from this file:

- macOS/Linux: `~/.codex/.local-data/codex-plugins-kit/.venv/bin/llm-scripting-kit endpoints`
- Windows: `%USERPROFILE%\.codex\.local-data\codex-plugins-kit\.venv\Scripts\llm-scripting-kit.exe endpoints`

The canonical library reads the existing Claude configuration and credentials,
so do not copy keys or create a second endpoint registry. Use `models`, then
`resolve`, when endpoint or model selection needs more detail. Dispatch a
bounded external unit with `complete --format json`, sending its standalone
brief over stdin or a UTF-8 file. HTTP endpoints and Claude, Codex, and OpenCode
harnesses are all valid. A user-named backend or model takes precedence.

Use a Codex CLI harness when its configured model, effort, isolated process, or
explicit selection is useful. Do not route ordinary Codex fan-out through the
CLI when native background agents provide the same capability more efficiently.

See [references/delegation.md](references/delegation.md) for unit design and
verification rules.

## Procedure

1. Confirm the task warrants orchestration. Delegate multiple independent
   units or work that reads/emits much more material than its conclusion. Keep
   a small self-contained unit inline.
2. Discover configured LLM endpoints. Treat discovery output plus currently
   available native background-agent facilities as the runtime source of truth.
3. Decompose the task. Record dependencies and assign one owner to every file.
   Independent units run concurrently; dependent units wait.
4. Route each unit. Prefer native Codex agents for ordinary repository work;
   choose a configured external model or harness for a requested model, an
   independent critique, different capabilities, or deliberate isolation.
5. Give every unit a standalone brief containing its goal, paths, constraints,
   premises, required checks, and return shape. Label each premise as
   `established` with evidence or `hypothesis`.
6. A hypothesis may fund investigation, never mutation. Require the delegate
   to verify it before changing anything and to halt if it is refuted.
7. While units run, coordinate only. Send changed constraints to affected
   native agents. For a CLI/HTTP call with no follow-up channel, cancel and
   relaunch it or explicitly re-verify its stale result.
8. Synthesize concise reports. Inspect actual diffs and test results before
   accepting file-writing work. Cross-check disagreements rather than choosing
   whichever result arrived first.
9. Tell the user what was completed, what was verified, and what remains
   uncertain. Do not expose credentials or internal raw output.

## External dispatch contract

For each `llm-scripting-kit complete` call:

- Put substantial prompts in stdin or a temporary UTF-8 file, never argv.
- Request JSON and read the answer from `response.text`.
- Exit code 2 means the request/configuration is invalid; correct it.
- Exit code 3 is a persistent halt such as authentication, credit, or rate
  limiting; report the classified cause.
- Exit code 1 is an execution failure. Apply the planned fallback or report it.
- Do not claim an absent endpoint is globally unavailable; report only what
  discovery found in the active configuration.
