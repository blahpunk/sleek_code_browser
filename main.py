import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

from styles import apply_styles
from ui_logic import UiLogic
from ui_setup import UiSetup


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # pylint: disable=protected-access
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class FileBrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_setup = UiSetup(self)
        apply_styles(self)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.initUI()
        self.ui_logic = UiLogic(self.ui_setup)

    def initUI(self):
        self.setWindowTitle("Sleek Code Browser")
        self.setGeometry(100, 100, 1080, 760)

    def closeEvent(self, event):
        self.ui_logic.save_ui_state()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))
    window = FileBrowserApp()
    cli_path = sys.argv[1] if len(sys.argv) > 1 else ""
    if cli_path:
        requested_path = os.path.abspath(cli_path)
        if os.path.isfile(requested_path):
            requested_path = os.path.dirname(requested_path)
        if os.path.isdir(requested_path):
            window.ui_logic.open_folder(requested_path)
    window.show()
    sys.exit(app.exec_())
