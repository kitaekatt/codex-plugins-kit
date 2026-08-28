---
name: task
description: Manage file-backed project tasks using the canonical Awesome Kit task system. Use when creating, listing, working, updating, closing, reopening, archiving, deleting, moving, validating, showing, or summarizing task folders and task_list references. Do not use for Codex's native plan or task tracking.
---

# Task

This is a thin Codex adapter over the canonical task system in the editable `plugins-kit` checkout. The upstream implementation owns all task behavior and continues to use `CLAUDE.md` so the same task folders interoperate with Claude Code. Do not copy, reinterpret, or edit task-system behavior in this plugin.

## Before operating

Read the complete canonical task instructions at:

`<pluginsKit>/plugins/awesome-kit/skills/task/SKILL.md`

Resolve `<pluginsKit>` from the `pluginsKit` field in:

`~/.codex/.local-data/codex-plugins-kit/runtime.json`

Read any canonical reference that those instructions require for the requested verb, especially `references/handoff-template.md` for `init`, substantive `update`, or hand-off packaging. Those upstream files are the authoritative operating contract.

## Invoke the adapter

Run from the project root. Use the shared runtime's Python and this plugin's `scripts/task.py` launcher:

- macOS/Linux Python: `~/.codex/.local-data/codex-plugins-kit/.venv/bin/python`
- Windows Python: `%USERPROFILE%\.codex\.local-data\codex-plugins-kit\.venv\Scripts\python.exe`
- Launcher: `<awesome-kit-plugin-root>/scripts/task.py`

Pass the canonical verb and arguments unchanged:

```text
python task.py <verb> [args]
```

All 13 canonical verbs are available: `init`, `list`, `show`, `status`, `validate`, `work`, `update`, `items`, `close`, `reopen`, `archive`, `delete`, and `move`. Exit codes, stdout/stderr, task discovery, Git behavior, and file formats are the upstream CLI's contract.

## Codex work behavior

For `work`, the adapter converts upstream `Skill(skill: "name")` output to Codex-native `$name` lines while preserving each stored skill identity, including `awesome-kit:orchestrate`.

Use every emitted `$skill-name` in order. Then obey the final dispatch directive. For `awesome-kit:orchestrate`, use the installed Codex Awesome Kit orchestration skill and native Codex background agents. Honor an emitted `agent_hint`. Do not replace ordinary native background-agent delegation with nested `codex exec`; the orchestration skill decides when an LLM endpoint or CLI harness is useful.

For `status`, the CLI emits substrate rather than prose. Delegate a concise background-agent summary from that substrate as required by the canonical skill.

When `update` packages a hand-off, keep the canonical two-line baton and `CLAUDE.md` interoperability contract exactly as documented upstream.
