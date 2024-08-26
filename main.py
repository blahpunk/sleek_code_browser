import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_logic import UiLogic
from ui_setup import UiSetup
from styles import apply_styles

class FileBrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_setup = UiSetup(self)
        self.ui_logic = UiLogic(self.ui_setup)  # Only pass the ui_setup now
        apply_styles(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sleek File Browser')
        self.setGeometry(100, 100, 800, 600)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileBrowserApp()
    ex.show()
    sys.exit(app.exec_())
