# Local CP (Local Copilot)

Local CP is a local-first Windows desktop application for exploring codebases and
running lightweight static analysis. The first milestone works without accounts,
API keys, or network access.

## Milestone 1 features

- Open a local project with a native directory picker.
- Browse its files and folders in a tree.
- View text files without modifying them.
- See file, directory, size, and language statistics.
- Analyze Python classes, functions, methods, and imports with `ast`.
- Keep project scanning and analysis off the GUI thread.
- Report binary, oversized, unreadable, and invalid Python files clearly.

## Requirements

- Windows 11
- Python 3.11 or newer

## Setup and run

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m local_cp
```

You can also launch the installed `local-cp` command.

## Test and lint

```powershell
pytest
ruff check .
```

## Usage

1. Select **Open Project** and choose a repository or source directory.
2. Select a file in the left panel to view it.
3. Select a Python file and press **Analyze Python File**.
4. Review project statistics and analysis in the right-side tabs.

Large files (over 2 MiB) are not displayed. Common generated directories such as
`.git`, `.venv`, `node_modules`, `build`, and `dist` are excluded from project
statistics, but remain visible in the file tree.

See [docs/architecture.md](docs/architecture.md) for design decisions, limitations,
and the next milestone.

