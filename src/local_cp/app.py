from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from local_cp.analysis.python_analyzer import analyze_python_source
from local_cp.gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Local CP")
    app.setOrganizationName("Local CP")

    window = MainWindow()
    window.show()
    if sys.argv[1:] == ["--smoke-test"]:
        # Exercise Qt startup and the bundled analysis module without making a network request.
        result = analyze_python_source("import pathlib\nclass Sample:\n    pass\n")
        if result.syntax_error or len(result.classes) != 1 or result.imports != ["pathlib"]:
            return 1
        QTimer.singleShot(100, app.quit)
    return app.exec()
