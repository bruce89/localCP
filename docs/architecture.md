# Architecture

## Goals

Local CP is local-first: repository contents remain on the machine unless a user
explicitly selects context and submits an AI request. Milestone 1 performs no
network operations.

## Components

- `gui`: Qt widgets, presentation, actions, and background-work coordination.
- `project`: directory traversal, file classification, safe text reads, and statistics.
- `analysis`: deterministic analyzers and typed result models.
- `config`: persisted non-secret desktop preferences.
- `ai`: provider boundary reserved for milestone 2. It has no implementation yet.

The GUI consumes results from `project` and `analysis`; those packages do not import
Qt. This keeps core behavior independently testable and prevents a future AI provider
from becoming coupled to presentation code.

## Concurrency

Project scans and Python parsing run through `QThreadPool`. Results and failures are
returned to the main thread with Qt signals. The filesystem tree uses Qt's asynchronous
`QFileSystemModel`.

## Safety boundaries

- Common generated and metadata directories are excluded from aggregate scans.
- Symbolic-link directories are not followed during scans.
- Binary files are not decoded or displayed.
- Files larger than 2 MiB are not loaded into the viewer or analyzer.
- Syntax errors are represented as analysis results rather than crashing the UI.
- No repository content is sent over the network.

## Current limitations

- Static structure extraction is Python-specific.
- Language detection is extension-based.
- The code viewer has no syntax highlighting or editing support.
- Ignored directories are fixed defaults rather than `.gitignore` aware.
- There is no packaged Windows executable yet.

## Next milestone: optional AI assistance

1. Add a provider protocol independent of the GUI.
2. Implement an OpenAI-compatible HTTP provider with configurable endpoint and model.
3. Store API credentials through the OS credential store.
4. Add explicit context selection and preview before submission.
5. Enforce configurable byte and estimated-token budgets.
6. Show exactly which files will leave the machine and require an explicit Send action.
7. Add mocked provider tests; keep all core features usable without credentials.

