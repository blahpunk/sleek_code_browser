import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow

from ui_logic import UiLogic
from ui_setup import UiSetup

APP_NAME = "Sleek Code Browser"


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # pylint: disable=protected-access
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def read_version():
    version_file = resource_path("VERSION")
    try:
        with open(version_file, "r", encoding="utf-8") as handle:
            version = handle.read().strip()
    except OSError:
        return ""
    return version


def resolve_startup_folder(argv):
    explicit_path = argv[1].strip() if len(argv) > 1 else ""
    if explicit_path:
        requested_path = os.path.abspath(os.path.expanduser(explicit_path))
        if os.path.isfile(requested_path):
            requested_path = os.path.dirname(requested_path)
        if os.path.isdir(requested_path):
            return requested_path

    try:
        current_working_directory = os.getcwd()
    except OSError:
        current_working_directory = ""

    if current_working_directory and os.path.isdir(current_working_directory):
        return os.path.abspath(current_working_directory)
    return ""


class FileBrowserApp(QMainWindow):
    def __init__(self, startup_folder=""):
        super().__init__()
        self.version = read_version()
        self.app_title = APP_NAME if not self.version else f"{APP_NAME} v{self.version}"
        self.ui_setup = UiSetup(self)
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.initUI()
        self.ui_logic = UiLogic(self.ui_setup, startup_folder=startup_folder, app_title=self.app_title)

    def initUI(self):
        self.setWindowTitle(self.app_title)
        self.setGeometry(100, 100, 1080, 760)

    def closeEvent(self, event):
        self.ui_logic.save_ui_state()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))
    startup_folder = resolve_startup_folder(sys.argv)
    window = FileBrowserApp(startup_folder=startup_folder)
    window.show()
    sys.exit(app.exec_())
