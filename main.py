# main.py

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from ui_logic import UiLogic
from ui_setup import UiSetup
from styles import apply_styles


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class FileBrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_setup = UiSetup(self)
        self.ui_logic = UiLogic(self.ui_setup)
        apply_styles(self)
        self.setWindowIcon(QIcon(resource_path('icon.ico')))  # Use bundled icon
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sleek Code Browser')
        self.setGeometry(100, 100, 800, 600)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileBrowserApp()
    ex.show()
    sys.exit(app.exec_())
