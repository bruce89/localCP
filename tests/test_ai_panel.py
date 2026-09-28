from __future__ import annotations

import os
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication  # noqa: E402

from local_cp.ai.models import AIResponse, CodeContext  # noqa: E402
from local_cp.gui.ai_panel import AIPanel  # noqa: E402


class FakeSettings:
    def provider_base_url(self) -> str:
        return "https://example.test/v1/"

    def provider_model(self) -> str:
        return "test-model"

    def set_provider(self, base_url: str, model: str) -> None:
        assert base_url == "https://example.test/v1/"
        assert model == "test-model"


def test_two_files_require_preview_and_explicit_send(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"
    first.write_text("FIRST = 1\n", encoding="utf-8")
    second.write_text("SECOND = 2\n", encoding="utf-8")
    calls: list[tuple[str, CodeContext]] = []

    class FakeAssistant:
        def ask(
            self, question: str, context: CodeContext, *, base_url: str, model: str
        ) -> AIResponse:
            calls.append((question, context))
            return AIResponse("Both files define constants.", model)

    panel = AIPanel(FakeSettings())  # type: ignore[arg-type]
    panel._assistant = FakeAssistant()  # type: ignore[assignment]
    panel.set_selection(tmp_path, first)
    panel._add_button.click()
    panel.set_selection(tmp_path, second)
    panel._add_button.click()
    assert calls == []
    assert not panel._send_button.isEnabled()

    panel._question.setPlainText("Compare the files")
    panel._prepare_button.click()
    assert panel._send_button.isEnabled()
    assert panel._preview.toPlainText().count("File: ") == 2
    assert "FIRST = 1" in panel._preview.toPlainText()
    assert "SECOND = 2" in panel._preview.toPlainText()
    panel.set_selection(tmp_path, first)
    assert panel._send_button.isEnabled()
    assert not panel._add_button.isEnabled()

    panel._send_button.click()
    deadline = time.monotonic() + 5
    while panel._worker is not None and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    assert panel._worker is None
    assert len(calls) == 1
    assert [file.relative_path for file in calls[0][1].files] == ["first.py", "second.py"]
    assert "Both files define constants." in panel._response.toPlainText()
    panel._question.setPlainText("A different question")
    assert not panel._send_button.isEnabled()
    panel.close()


def test_removing_file_invalidates_preview(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    first = tmp_path / "first.py"
    first.write_text("FIRST = 1\n", encoding="utf-8")
    panel = AIPanel(FakeSettings())  # type: ignore[arg-type]
    panel.set_selection(tmp_path, first)
    panel._add_button.click()
    panel._question.setPlainText("Explain")
    panel._prepare_button.click()
    assert panel._send_button.isEnabled()

    panel._remove_button.click()
    app.processEvents()
    assert panel._files_list.count() == 0
    assert not panel._send_button.isEnabled()
    assert panel._preview.toPlainText() == ""
    panel.close()


def test_flagged_context_requires_explicit_acknowledgement(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    source = tmp_path / "config.py"
    source.write_text('API_KEY = "sample-secret-value"\n', encoding="utf-8")
    calls: list[CodeContext] = []

    class FakeAssistant:
        def ask(
            self, question: str, context: CodeContext, *, base_url: str, model: str
        ) -> AIResponse:
            calls.append(context)
            return AIResponse("Answer", model)

    panel = AIPanel(FakeSettings())  # type: ignore[arg-type]
    panel._assistant = FakeAssistant()  # type: ignore[assignment]
    panel.set_selection(tmp_path, source)
    panel._add_button.click()
    panel._question.setPlainText("Explain")
    panel._prepare_button.click()

    assert not panel._warning.isHidden()
    assert "config.py:1" in panel._warning.text()
    assert "sample-secret-value" not in panel._warning.text()
    assert not panel._send_button.isEnabled()
    panel._send_button.click()
    assert calls == []

    panel._acknowledge.setChecked(True)
    assert panel._send_button.isEnabled()
    panel._send_button.click()
    deadline = time.monotonic() + 5
    while panel._worker is not None and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()
    assert len(calls) == 1
    panel._question.setPlainText("New question")
    assert not panel._send_button.isEnabled()
    assert not panel._acknowledge.isChecked()
    panel.close()
