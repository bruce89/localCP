from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from local_cp.ai.context import MAX_FILES, build_user_message, prepare_context
from local_cp.ai.models import AIResponse, CodeContext
from local_cp.ai.secret_scan import SecretFinding, scan_request
from local_cp.ai.service import AssistantService
from local_cp.config.settings import AppSettings
from local_cp.gui.workers import Worker


class AIPanel(QWidget):
    """Explicit file list and preview-before-send flow."""

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self._settings = settings
        self._assistant = AssistantService()
        self._root: Path | None = None
        self._selected: Path | None = None
        self._included: list[Path] = []
        self._prepared: CodeContext | None = None
        self._prepared_question: str | None = None
        self._findings: tuple[SecretFinding, ...] = ()
        self._worker: Worker | None = None

        self._file_label = QLabel("Select a Python file.")
        self._file_label.setWordWrap(True)
        self._add_button = QPushButton("Add selected file")
        self._add_button.setEnabled(False)
        self._add_button.clicked.connect(self._add_selected)
        self._remove_button = QPushButton("Remove highlighted file")
        self._remove_button.setEnabled(False)
        self._remove_button.clicked.connect(self._remove_highlighted)
        self._files_list = QListWidget()
        self._files_list.setMaximumHeight(90)
        self._files_list.currentRowChanged.connect(lambda _row: self._update_controls())
        self._url = QLineEdit(settings.provider_base_url())
        self._model = QLineEdit(settings.provider_model())
        self._question = QPlainTextEdit()
        self._question.setPlaceholderText("What does this file do? Highlight one potential issue.")
        self._question.setMaximumHeight(90)
        self._question.textChanged.connect(self._invalidate_preview)
        self._preview = QPlainTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setPlaceholderText("Prepare context to review the exact file content.")
        self._response = QPlainTextEdit()
        self._response.setReadOnly(True)
        self._response.setPlaceholderText("The provider response will appear here.")
        self._budget = QLabel(
            f"Up to {MAX_FILES} .py files, 12 KB combined; estimated input limit 4,000 tokens."
        )
        self._budget.setWordWrap(True)
        self._prepare_button = QPushButton("Prepare context")
        self._prepare_button.setEnabled(False)
        self._prepare_button.clicked.connect(self._prepare)
        self._send_button = QPushButton("Send previewed files and question")
        self._send_button.setEnabled(False)
        self._send_button.clicked.connect(self._send)
        self._warning = QLabel()
        self._warning.setWordWrap(True)
        self._warning.setVisible(False)
        self._warning.setStyleSheet("color: #9b3b12; font-weight: 600;")
        self._acknowledge = QCheckBox("I reviewed the flagged lines and choose to send")
        self._acknowledge.setVisible(False)
        self._acknowledge.toggled.connect(self._update_send_button)

        form = QFormLayout()
        form.addRow("Base URL", self._url)
        form.addRow("Model", self._model)
        layout = QVBoxLayout(self)
        layout.addWidget(self._file_label)
        buttons = QHBoxLayout()
        buttons.addWidget(self._add_button)
        buttons.addWidget(self._remove_button)
        layout.addLayout(buttons)
        layout.addWidget(self._files_list)
        layout.addLayout(form)
        layout.addWidget(QLabel("Question"))
        layout.addWidget(self._question)
        layout.addWidget(self._budget)
        layout.addWidget(self._prepare_button)
        layout.addWidget(QLabel("Exact question and source to send — review for secrets"))
        layout.addWidget(self._preview, 1)
        layout.addWidget(self._warning)
        layout.addWidget(self._acknowledge)
        layout.addWidget(self._send_button)
        layout.addWidget(QLabel("Answer"))
        layout.addWidget(self._response, 1)

    def set_selection(self, root: Path | None, selected: Path | None) -> None:
        if root != self._root:
            self._included.clear()
            self._files_list.clear()
            self._invalidate_preview()
        self._root = root
        self._selected = selected
        self._file_label.setText(str(selected) if selected else "Select a Python file.")
        self._update_controls()

    def _update_controls(self) -> None:
        selected = self._selected
        self._add_button.setEnabled(
            selected is not None
            and selected.suffix.lower() == ".py"
            and selected.resolve() not in self._included
            and len(self._included) < MAX_FILES
        )
        self._remove_button.setEnabled(self._files_list.currentRow() >= 0)
        self._prepare_button.setEnabled(bool(self._included))

    def _add_selected(self) -> None:
        if self._root is None or self._selected is None:
            return
        try:
            if self._selected.is_symlink():
                raise ValueError("Symbolic-link files are not available as AI context.")
            path = self._selected.resolve(strict=True)
            root = self._root.resolve(strict=True)
            if not path.is_file() or path.suffix.lower() != ".py":
                raise ValueError("Choose a Python (.py) file.")
            if not path.is_relative_to(root):
                raise ValueError("The selected file is outside the open project.")
            if path in self._included:
                raise ValueError("That file is already in the context list.")
            if len(self._included) >= MAX_FILES:
                raise ValueError(f"Choose at most {MAX_FILES} files.")
        except (OSError, ValueError) as error:
            self._show_error(str(error))
            return
        self._included.append(path)
        self._files_list.addItem(path.relative_to(root).as_posix())
        self._files_list.setCurrentRow(self._files_list.count() - 1)
        self._update_controls()
        self._invalidate_preview()

    def _remove_highlighted(self) -> None:
        row = self._files_list.currentRow()
        if row < 0:
            return
        del self._included[row]
        self._files_list.takeItem(row)
        self._update_controls()
        self._invalidate_preview()

    def _invalidate_preview(self) -> None:
        self._prepared = None
        self._prepared_question = None
        self._findings = ()
        self._preview.clear()
        self._warning.clear()
        self._warning.setVisible(False)
        self._acknowledge.setChecked(False)
        self._acknowledge.setVisible(False)
        self._update_send_button()
        self._budget.setText(
            f"{len(self._included)}/{MAX_FILES} .py files selected; "
            "12 KB combined, estimated input limit 4,000 tokens."
        )

    def _prepare(self) -> None:
        if self._root is None or not self._included:
            return
        question = self._question.toPlainText().strip()
        try:
            context = prepare_context(self._root, self._included, question)
        except (OSError, ValueError) as error:
            self._show_error(str(error))
            return
        self._prepared = context
        self._prepared_question = question
        self._findings = scan_request(question, context)
        self._preview.setPlainText(build_user_message(question, context.files))
        self._budget.setText(
            f"{len(context.files)} file(s) · ~{context.estimated_input_tokens:,} input tokens "
            "(conservative estimate; actual usage may differ)."
        )
        self._acknowledge.setChecked(False)
        if self._findings:
            locations = ", ".join(
                f"{finding.location}:{finding.line} ({finding.reason})"
                for finding in self._findings[:5]
            )
            more = f" (+{len(self._findings) - 5} more)" if len(self._findings) > 5 else ""
            self._warning.setText(
                f"Possible secrets found locally: {locations}{more}. "
                "Review the preview before sending. Detection is incomplete."
            )
            self._warning.setVisible(True)
            self._acknowledge.setVisible(True)
        else:
            self._warning.clear()
            self._warning.setVisible(False)
            self._acknowledge.setVisible(False)
        self._update_send_button()

    def _update_send_button(self) -> None:
        self._send_button.setEnabled(
            self._prepared is not None
            and self._worker is None
            and (not self._findings or self._acknowledge.isChecked())
        )

    def _send(self) -> None:
        context = self._prepared
        question = self._prepared_question
        if (
            context is None
            or question is None
            or self._worker is not None
            or (self._findings and not self._acknowledge.isChecked())
        ):
            return
        self._settings.set_provider(self._url.text(), self._model.text())
        self._response.setPlainText("Waiting for provider…")
        self._send_button.setEnabled(False)
        base_url = self._url.text()
        model = self._model.text()
        worker = Worker(
            lambda: self._assistant.ask(question, context, base_url=base_url, model=model)
        )
        self._worker = worker
        worker.signals.succeeded.connect(self._show_response)
        worker.signals.failed.connect(self._show_error)
        worker.signals.finished.connect(self._finish_request)
        QThreadPool.globalInstance().start(worker)

    def _show_response(self, response: AIResponse) -> None:
        usage = ""
        if response.input_tokens is not None or response.output_tokens is not None:
            usage = (
                f"\n\nModel: {response.model} · Input tokens: {response.input_tokens} · "
                f"Output tokens: {response.output_tokens}"
            )
        self._response.setPlainText(response.text + usage)

    def _finish_request(self) -> None:
        self._worker = None
        self._update_send_button()

    def _show_error(self, message: str) -> None:
        self._response.setPlainText(message)
        QMessageBox.warning(self, "Local CP AI", message)
