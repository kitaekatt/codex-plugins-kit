# Architecture

`plugins-kit` owns reusable behavior. `codex-plugins-kit` owns Codex packaging, host instructions, setup, and compatibility checks.

```text
Codex plugin/skill
    -> shared managed Python runtime
    -> editable plugins-kit packages
    -> canonical endpoint, orchestration, or task behavior
```

## Runtime contract

- Runtime root: `~/.codex/.local-data/codex-plugins-kit/`
- Virtual environment: `<runtime-root>/.venv`
- Development source: auto-detected sibling `../plugins-kit`, or `--plugins-kit PATH`
- Public fallback source: managed checkout pinned by `upstream.lock.json`
- Installation mode: editable for local and managed checkouts
- Platforms: macOS, Linux, and Windows
- Configuration: existing `plugins-kit` configuration and credentials remain in their current locations
- Lifecycle: repository-level `setup`, `doctor`, and runtime-only `uninstall`

## Package sets

| Adapter | Editable upstream packages |
| --- | --- |
| `llm-scripting-kit` | `bootstrap`, `llm-scripting-kit[sdk]` |
| `awesome-kit` | `bootstrap`, `llm-scripting-kit[sdk]`, `skills-kit` |

The bootstrap package is installed only as a library dependency. The Claude bootstrap lifecycle is not executed.

## Awesome host boundary

The Awesome adapter will expose only `orchestrate` and `task`. It must call upstream behavior through public interfaces and host-profile seams rather than copying implementation. For initial interoperability, task context continues to use `CLAUDE.md`. Native Codex background agents remain the preferred Codex-native orchestration mechanism, while all configured llm-scripting-kit HTTP endpoints and CLI harnesses must remain usable.

The exact skill behavior is deliberately deferred until the upstream interfaces are finalized.
