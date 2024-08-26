import os
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTreeWidgetItem

class FileLoader(QThread):
    update_tree = pyqtSignal(object, str)
    loading_done = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = None
        self.folder_path = ""

    def setParams(self, root_item, folder_path):
        self.root_item = root_item
        self.folder_path = folder_path

    def run(self):
        self.addTreeItems(self.root_item, self.folder_path)
        self.loading_done.emit()

    def addTreeItems(self, parentItem, folderPath):
        try:
            for fileName in sorted(os.listdir(folderPath)):
                filePath = os.path.join(folderPath, fileName)
                item = QTreeWidgetItem(parentItem, [fileName])
                item.setCheckState(0, Qt.Checked)
                if os.path.isdir(filePath):
                    item.setIcon(0, QIcon.fromTheme("folder"))
                    item.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                    item.setData(0, Qt.UserRole, filePath)
                else:
                    item.setIcon(0, QIcon.fromTheme("text-x-generic"))
                self.update_tree.emit(item, filePath)
        except Exception as e:
            print(f"Error loading directory {folderPath}: {e}")
