from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from local_cp.ai.context import prepare_context
from local_cp.ai.models import AIResponse, CodeContext
from local_cp.ai.service import AssistantService
from local_cp.config.settings import AppSettings
from local_cp.gui.workers import Worker


class AIPanel(QWidget):
    """One-file, preview-before-send experiment. No request starts on selection."""

    def __init__(self, settings: AppSettings) -> None:
        super().__init__()
        self._settings = settings
        self._assistant = AssistantService()
        self._root: Path | None = None
        self._selected: Path | None = None
        self._prepared: CodeContext | None = None
        self._prepared_question: str | None = None
        self._worker: Worker | None = None

        self._file_label = QLabel("Select a Python file.")
        self._file_label.setWordWrap(True)
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
        self._budget = QLabel("One .py file, up to 12 KB; estimated input limit 4,000 tokens.")
        self._budget.setWordWrap(True)
        self._prepare_button = QPushButton("Prepare context")
        self._prepare_button.setEnabled(False)
        self._prepare_button.clicked.connect(self._prepare)
        self._send_button = QPushButton("Send previewed file and question")
        self._send_button.setEnabled(False)
        self._send_button.clicked.connect(self._send)

        form = QFormLayout()
        form.addRow("Base URL", self._url)
        form.addRow("Model", self._model)
        layout = QVBoxLayout(self)
        layout.addWidget(self._file_label)
        layout.addLayout(form)
        layout.addWidget(QLabel("Question"))
        layout.addWidget(self._question)
        layout.addWidget(self._budget)
        layout.addWidget(self._prepare_button)
        layout.addWidget(QLabel("Exact source to send — review for secrets"))
        layout.addWidget(self._preview, 1)
        layout.addWidget(self._send_button)
        layout.addWidget(QLabel("Answer"))
        layout.addWidget(self._response, 1)

    def set_selection(self, root: Path | None, selected: Path | None) -> None:
        self._root = root
        self._selected = selected
        self._file_label.setText(str(selected) if selected else "Select a Python file.")
        self._prepare_button.setEnabled(selected is not None and selected.suffix.lower() == ".py")
        self._invalidate_preview()

    def _invalidate_preview(self) -> None:
        self._prepared = None
        self._prepared_question = None
        self._preview.clear()
        self._send_button.setEnabled(False)

    def _prepare(self) -> None:
        if self._root is None or self._selected is None:
            return
        question = self._question.toPlainText().strip()
        try:
            context = prepare_context(self._root, self._selected, question)
        except (OSError, ValueError) as error:
            self._show_error(str(error))
            return
        self._prepared = context
        self._prepared_question = question
        self._preview.setPlainText(context.source)
        self._budget.setText(
            f"{context.relative_path} · ~{context.estimated_input_tokens:,} input tokens "
            "(conservative estimate; actual usage may differ)."
        )
        self._send_button.setEnabled(self._worker is None)

    def _send(self) -> None:
        context = self._prepared
        question = self._prepared_question
        if context is None or question is None or self._worker is not None:
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
        self._send_button.setEnabled(self._prepared is not None)

    def _show_error(self, message: str) -> None:
        self._response.setPlainText(message)
        QMessageBox.warning(self, "Local CP AI", message)
