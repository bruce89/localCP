# Local CP (Local Copilot)

Local CP is a local-first Windows desktop application for exploring codebases,
running lightweight static analysis, and optionally asking about up to three
explicitly chosen Python files through an OpenAI-compatible API. Local analysis
needs no API key.

## Current features

- Open a local project with a native directory picker.
- Browse its files and folders in a tree.
- View text files without modifying them.
- See file, directory, size, and language statistics.
- Analyze Python classes, functions, methods, and imports with `ast`.
- Keep project scanning and analysis off the GUI thread.
- Report binary, oversized, unreadable, and invalid Python files clearly.
- Prepare an explicit, previewed AI question using up to three selected Python files.
- Warn locally about some likely secrets before an optional external send.
- Build a portable Windows ZIP; source use and local analysis remain possible without AI credentials.

## Requirements

- Windows 11
- Python 3.11 or newer to run from source; the portable ZIP includes Python.

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

## Portable Windows build

The optional packaging tools are only needed on the machine building the app:

```powershell
python -m pip install -e ".[dev,package]"
.\scripts\build_windows.ps1 -Python ".\.venv\Scripts\python.exe"
```

The script creates `dist\LocalCP-windows-x64.zip` and checks that the extracted
`LocalCP.exe` starts with Python removed from its process `PATH`. Unzip the whole
`LocalCP` folder anywhere on Windows 11 and run `LocalCP.exe`; do not move the EXE
out of its folder. The app still works locally without API credentials. For build,
test, and distribution details, see [docs/packaging.md](docs/packaging.md).

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

1. Open a project, select a `.py` file, and choose **Add selected file** in the
   **AI** tab. Repeat for up to three files. Remove a highlighted file if needed.
2. Enter a question and choose **Prepare context**.
3. Inspect the complete question and the exact source of every included file.
   Review it for secrets or anything you do not want to share.
4. Choose **Send previewed files and question**. This is the only action that
   sends source code to the configured provider.

If a local scan finds a possible credential in the question or source, Local CP
shows its location and asks you to acknowledge the warning before Send is enabled.
It does not display the matched value in the warning. The scan is advisory and
cannot prove that a file is free of secrets; review the full preview yourself.

The current experiment allows at most 12 KB of source **across all files**,
estimates at most 4,000 input tokens, and requests at most 384 output tokens.
Changing the question or file list clears the preview; prepare it again before
sending. There is no automatic retry.
Google's actual rate limits vary by project, tier, and model; check your active
limits in [AI Studio](https://ai.google.dev/gemini-api/docs/rate-limits).

Large files (over 2 MiB) are not displayed. Common generated directories such as
`.git`, `.venv`, `node_modules`, `build`, and `dist` are excluded from project
statistics, but remain visible in the file tree.

See [docs/architecture.md](docs/architecture.md) for the evolving Mermaid diagram
and design decisions, and [docs/SPEC.md](docs/SPEC.md) for iteration tracking.

For a guided introduction to Python and hands-on exercises using this codebase,
start with [LearnDocs](LearnDocs/README.md).
