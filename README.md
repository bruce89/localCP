# Local CP (Local Copilot)

Local CP is a local-first Windows desktop application for exploring codebases,
running lightweight static analysis, and optionally asking about one selected
Python file through an OpenAI-compatible API. Local analysis needs no API key.

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

## Optional AI experiment

The AI tab defaults to the Google AI Studio compatible endpoint and the
`gemini-3.5-flash-lite` model requested for this experiment. Both fields are
editable; no model name is embedded in the HTTP provider. Set `GEMINI_API_KEY`
as a Windows user environment variable. Local CP reads it at send time, including
when the current process has not inherited newly created user variables. The key
is never written to project files or application settings.

1. Open a project and select one `.py` file.
2. Enter a question in the **AI** tab.
3. Choose **Prepare context** and inspect the exact source shown. Review it for
   secrets or anything you do not want to share.
4. Choose **Send previewed file and question**. This is the only action that
   sends source code to the configured provider.

The first experiment allows at most 12 KB of source, estimates at most 4,000 input
tokens, and requests at most 384 output tokens. There is no automatic retry.
Google's actual rate limits vary by project, tier, and model; check your active
limits in [AI Studio](https://ai.google.dev/gemini-api/docs/rate-limits).

Large files (over 2 MiB) are not displayed. Common generated directories such as
`.git`, `.venv`, `node_modules`, `build`, and `dist` are excluded from project
statistics, but remain visible in the file tree.

See [docs/architecture.md](docs/architecture.md) for the evolving Mermaid diagram
and design decisions, and [docs/SPEC.md](docs/SPEC.md) for iteration tracking.
