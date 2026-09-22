from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from local_cp.gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Local CP")
    app.setOrganizationName("Local CP")

    window = MainWindow()
    window.show()
    return app.exec()
