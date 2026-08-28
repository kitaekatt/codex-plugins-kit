# codex-plugins-kit

Codex adapters for selected capabilities from [`plugins-kit`](https://github.com/kitaekatt/plugins-kit).

This repository is under initial development. Its adapters depend on canonical implementations maintained in `plugins-kit`; it does not aim to port every Claude Code plugin or duplicate their implementation.

## Shared runtime

The adapters use one managed Python 3.12 virtual environment at:

```text
~/.codex/.local-data/codex-plugins-kit/.venv
```

Every upstream package is installed editable. Setup automatically uses a sibling `../plugins-kit` checkout when available. Otherwise, it clones the immutable revision in `upstream.lock.json` into managed local data and installs that checkout editable.

Setup also registers this repository as the `codex-plugins-kit` marketplace and installs the selected Codex plugins. Pass `--skip-codex-install` when testing only the Python runtime.

On macOS or Linux:

```sh
./scripts/setup
./scripts/doctor
```

On Windows PowerShell:

```powershell
./scripts/setup.ps1
./scripts/doctor.ps1
```

Choose one plugin or an explicit source checkout when needed:

```sh
./scripts/setup --plugin llm-scripting-kit
./scripts/setup --plugins-kit /path/to/plugins-kit
```

`uv`, Git, and a Python 3 interpreter capable of launching the setup manager are required. `uv` provisions the managed Python 3.12 runtime.

`uninstall` removes only the managed virtual environment, managed source clone, and runtime record. It preserves credentials and user configuration.

## Initial adapters

- `llm-scripting-kit`: endpoint and harness delegation through the canonical upstream library.
- `awesome-kit`: selected `orchestrate` and `task` capabilities. Capability content is not yet implemented.

MCP is intentionally out of scope.
