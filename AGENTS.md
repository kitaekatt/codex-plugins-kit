# codex-plugins-kit

This repository creates Codex adapters for selected Claude Code plugins maintained in the sibling `plugins-kit` repository.

This is the **Codex-first** sibling. Agent guidance lives in `AGENTS.md`. This repository deliberately has no `CLAUDE.md`.

The sibling `../plugins-kit` repository is Claude-first. Its `CLAUDE.md` contains the corresponding ownership rules.

## Purpose

- Expose selected `plugins-kit` capabilities to Codex.
- Keep reusable implementation in `plugins-kit`.
- Make necessary upstream changes in `plugins-kit` to improve interoperability and host-neutral reuse.
- Keep Codex plugins thin: packaging, Codex-specific instructions, setup, and host adaptation.
- Port only capabilities that are needed. Feature parity with every Claude plugin is not a goal.

## Architectural boundary

`plugins-kit` is the canonical source for reusable libraries and behavior.

`codex-plugins-kit` may contain:

- Codex plugin manifests
- Codex skills and instructions
- setup, launcher, and compatibility scripts
- Codex-specific host profiles and presentation
- tests for the adapter boundary

It should not copy or independently reimplement endpoint resolution, credential handling, orchestration policy, task-system behavior, or other reusable logic from `plugins-kit`.

When existing Claude plugin code is too host-specific to reuse, prefer a focused upstream change that introduces a host-neutral interface or host-profile seam.

## Upstream changes

Changes to `plugins-kit` are in scope when they:

- expose a stable public API or CLI;
- remove unnecessary Claude-specific assumptions from reusable code;
- make paths, terminology, or host behavior injectable;
- package reusable components for external installation;
- preserve existing Claude behavior.

Avoid broad refactors that are not required by an active Codex adapter.

## Adapter strategy

Each adapter should:

1. Use editable upstream packages. Public/managed checkouts use a pinned, immutable `plugins-kit` revision; local development uses the explicitly selected checkout.
2. Use public upstream APIs or CLIs.
3. Add only the Codex-specific behavior required for the selected capability.
4. Fail clearly when the installed upstream version is incompatible.
5. Avoid MCP unless it is explicitly brought into scope.

## Current scope

Initial adapters:

- `llm-scripting-kit`
- `awesome-kit`
  - `orchestrate`
  - `task`

Other Claude plugin capabilities are out of scope until explicitly selected.

## Stretch goal

Where practical, evolve Claude plugins toward the same adapter pattern:

- host-neutral core implementation;
- thin Claude adapter;
- thin Codex adapter.

This is a direction, not a prerequisite for shipping Codex support.

## Working across repositories

The expected local layout is:

```text
~/Dev/plugins-kit
~/Dev/codex-plugins-kit
```

When work requires an upstream change, make that change in `plugins-kit` rather than embedding a workaround or fork in `codex-plugins-kit`.
