from __future__ import annotations

import html
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import QDir, QModelIndex, Qt, QThreadPool
from PySide6.QtGui import QAction, QFontDatabase
from PySide6.QtWidgets import (
    QFileDialog,
    QFileSystemModel,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QSplitter,
    QTabWidget,
    QTextBrowser,
    QTreeView,
    QWidget,
)

from local_cp.analysis.models import PythonAnalysis
from local_cp.analysis.python_analyzer import analyze_python_file
from local_cp.config.settings import AppSettings
from local_cp.gui.ai_panel import AIPanel
from local_cp.gui.workers import Worker
from local_cp.project.explorer import read_text_file, scan_project
from local_cp.project.models import ProjectOverview


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Local CP")
        self.resize(1280, 760)

        self._settings = AppSettings()
        self._thread_pool = QThreadPool.globalInstance()
        self._workers: set[Worker] = set()
        self._project_root: Path | None = None
        self._selected_file: Path | None = None

        self._filesystem = QFileSystemModel(self)
        self._filesystem.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        )
        self._filesystem.setRootPath("")

        self._tree = QTreeView()
        self._tree.setModel(self._filesystem)
        self._tree.setHeaderHidden(False)
        self._tree.setAlternatingRowColors(True)
        self._tree.selectionModel().currentChanged.connect(self._selection_changed)
        for column in range(1, 4):
            self._tree.hideColumn(column)

        self._viewer = QPlainTextEdit()
        self._viewer.setReadOnly(True)
        self._viewer.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._viewer.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self._viewer.setPlaceholderText("Open a project, then select a text file.")

        self._overview = QTextBrowser()
        self._overview.setOpenExternalLinks(False)
        self._overview.setHtml("<h2>Project overview</h2><p>No project is open.</p>")
        self._analysis = QTextBrowser()
        self._analysis.setHtml(
            "<h2>Python analysis</h2><p>Select a Python file and choose Analyze.</p>"
        )
        self._ai_panel = AIPanel(self._settings)
        tabs = QTabWidget()
        tabs.addTab(self._overview, "Overview")
        tabs.addTab(self._analysis, "Analysis")
        tabs.addTab(self._ai_panel, "AI")

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._panel("Project", self._tree))
        splitter.addWidget(self._panel("Code", self._viewer))
        splitter.addWidget(tabs)
        splitter.setSizes([300, 620, 360])
        self.setCentralWidget(splitter)

        self._open_action = QAction("Open Project", self)
        self._open_action.setShortcut("Ctrl+O")
        self._open_action.triggered.connect(self._choose_project)
        self._analyze_action = QAction("Analyze Python File", self)
        self._analyze_action.setShortcut("Ctrl+R")
        self._analyze_action.setEnabled(False)
        self._analyze_action.triggered.connect(self._analyze_selected)
        toolbar = self.addToolBar("Project")
        toolbar.setMovable(False)
        toolbar.addAction(self._open_action)
        toolbar.addAction(self._analyze_action)

        self.statusBar().showMessage("Ready")

    @staticmethod
    def _panel(title: str, content: QWidget) -> QWidget:
        from PySide6.QtWidgets import QVBoxLayout

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(title)
        label.setStyleSheet("font-weight: 600; padding: 5px;")
        layout.addWidget(label)
        layout.addWidget(content)
        return panel

    def _choose_project(self) -> None:
        initial = self._settings.last_project()
        selected = QFileDialog.getExistingDirectory(
            self,
            "Open Project",
            str(initial) if initial else "",
            QFileDialog.Option.ShowDirsOnly,
        )
        if selected:
            self.open_project(Path(selected))

    def open_project(self, root: Path) -> None:
        root = root.resolve()
        self._project_root = root
        self._selected_file = None
        self._ai_panel.set_selection(root, None)
        self._settings.set_last_project(root)
        self._tree.setRootIndex(self._filesystem.index(str(root)))
        self._tree.setColumnWidth(0, 280)
        self._viewer.clear()
        self._viewer.setPlaceholderText("Select a text file to view it.")
        self._analysis.setHtml(
            "<h2>Python analysis</h2><p>Select a Python file and choose Analyze.</p>"
        )
        self._analyze_action.setEnabled(False)
        self.setWindowTitle(f"Local CP — {root.name}")
        self._overview.setHtml("<h2>Project overview</h2><p>Scanning…</p>")
        self.statusBar().showMessage(f"Scanning {root}…")
        self._start_worker(
            lambda: scan_project(root),
            self._show_overview,
            success_message="Project scan complete",
        )

    def _selection_changed(self, current: QModelIndex, _previous: QModelIndex) -> None:
        path = Path(self._filesystem.filePath(current))
        if not path.is_file():
            self._selected_file = None
            self._analyze_action.setEnabled(False)
            self._ai_panel.set_selection(self._project_root, None)
            return

        self._selected_file = path
        self._ai_panel.set_selection(self._project_root, path)
        self._analyze_action.setEnabled(path.suffix.lower() == ".py")
        try:
            text = read_text_file(path)
        except (OSError, ValueError) as error:
            self._viewer.setPlainText(f"Unable to display this file.\n\n{error}")
            self.statusBar().showMessage(str(error), 8000)
        else:
            self._viewer.setPlainText(text)
            self._viewer.document().setModified(False)
            self.statusBar().showMessage(str(path), 5000)

    def _analyze_selected(self) -> None:
        path = self._selected_file
        if path is None or path.suffix.lower() != ".py":
            self._show_error("Select a Python file before running analysis.")
            return
        self._analyze_action.setEnabled(False)
        self._analysis.setHtml("<h2>Python analysis</h2><p>Analyzing…</p>")
        self.statusBar().showMessage(f"Analyzing {path.name}…")
        self._start_worker(
            lambda: analyze_python_file(path),
            self._show_analysis,
            success_message=f"Analysis complete: {path.name}",
            when_finished=self._restore_analyze_action,
        )

    def _restore_analyze_action(self) -> None:
        self._analyze_action.setEnabled(
            self._selected_file is not None and self._selected_file.suffix.lower() == ".py"
        )

    def _start_worker(
        self,
        function: Callable[[], Any],
        on_success: Callable[[Any], None],
        *,
        success_message: str,
        when_finished: Callable[[], None] | None = None,
    ) -> None:
        worker = Worker(function)
        self._workers.add(worker)

        def succeeded(result: object) -> None:
            on_success(result)
            self.statusBar().showMessage(success_message, 5000)

        def finished() -> None:
            self._workers.discard(worker)
            if when_finished is not None:
                when_finished()

        worker.signals.succeeded.connect(succeeded)
        worker.signals.failed.connect(self._show_error)
        worker.signals.finished.connect(finished)
        self._thread_pool.start(worker)

    def _show_error(self, message: str) -> None:
        self.statusBar().showMessage(message, 10000)
        QMessageBox.warning(self, "Local CP", message)

    def _show_overview(self, overview: ProjectOverview) -> None:
        languages = (
            "".join(
                f"<li>{html.escape(language)}: {count:,}</li>"
                for language, count in overview.language_counts.items()
            )
            or "<li>No files detected</li>"
        )
        self._overview.setHtml(
            f"<h2>{html.escape(Path(overview.root).name)}</h2>"
            f"<p><b>Files:</b> {overview.file_count:,}<br>"
            f"<b>Directories:</b> {overview.directory_count:,}<br>"
            f"<b>Total size:</b> {self._format_size(overview.total_bytes)}<br>"
            f"<b>Skipped entries:</b> {overview.skipped_count:,}</p>"
            f"<h3>File types</h3><ul>{languages}</ul>"
        )

    def _show_analysis(self, analysis: PythonAnalysis) -> None:
        if analysis.syntax_error:
            self._analysis.setHtml(
                "<h2>Python analysis</h2>"
                f"<p><b>Syntax error:</b> {html.escape(analysis.syntax_error)}</p>"
            )
            return

        imports = "".join(f"<li>{html.escape(value)}</li>" for value in analysis.imports)
        functions = "".join(
            f"<li>{'async ' if item.is_async else ''}{html.escape(item.name)} "
            f"<small>(line {item.line})</small></li>"
            for item in analysis.functions
        )
        classes = []
        for item in analysis.classes:
            bases = f" ({html.escape(', '.join(item.bases))})" if item.bases else ""
            methods = (
                "".join(
                    f"<li>{'async ' if method.is_async else ''}{html.escape(method.name)} "
                    f"<small>(line {method.line})</small></li>"
                    for method in item.methods
                )
                or "<li><i>No methods</i></li>"
            )
            classes.append(
                f"<li><b>{html.escape(item.name)}</b>{bases} "
                f"<small>(line {item.line})</small><ul>{methods}</ul></li>"
            )

        self._analysis.setHtml(
            f"<h2>{html.escape(Path(analysis.path).name)}</h2>"
            f"<p><b>Lines:</b> {analysis.line_count:,}</p>"
            f"<h3>Imports ({len(analysis.imports)})</h3><ul>{imports or '<li>None</li>'}</ul>"
            f"<h3>Functions ({len(analysis.functions)})</h3>"
            f"<ul>{functions or '<li>None</li>'}</ul>"
            f"<h3>Classes ({len(analysis.classes)})</h3>"
            f"<ul>{''.join(classes) or '<li>None</li>'}</ul>"
        )

    @staticmethod
    def _format_size(byte_count: int) -> str:
        value = float(byte_count)
        for unit in ("B", "KiB", "MiB", "GiB"):
            if value < 1024 or unit == "GiB":
                return f"{value:,.0f} {unit}" if unit == "B" else f"{value:,.1f} {unit}"
            value /= 1024
        return f"{byte_count:,} B"
