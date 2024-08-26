import os
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

class DirectoryView(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)  # Hide the header for a cleaner look
        self.folder_path = ""  # Initialize the folder path attribute

    def populate(self, folderPath, default_checked_extensions=None):
        self.clear()  # Clear existing items
        self.folder_path = folderPath  # Store the folder path
        self.default_checked_extensions = default_checked_extensions if default_checked_extensions else []  # Store the default checked extensions
        self.addDirectoryItems(self.invisibleRootItem(), folderPath)

    def addDirectoryItems(self, parentItem, folderPath):
        try:
            for fileName in sorted(os.listdir(folderPath)):
                filePath = os.path.join(folderPath, fileName)
                item = QTreeWidgetItem(parentItem)
                item.setData(0, Qt.UserRole, filePath)  # Store the file path in the item

                if os.path.isdir(filePath):
                    item.setText(0, f"📁 {fileName}")
                    item.setCheckState(0, Qt.Checked)  # Folders are always checked by default
                    self.addDirectoryItems(item, filePath)  # Recursively add subdirectories
                else:
                    item.setText(0, f"📄 {fileName}")
                    file_extension = os.path.splitext(fileName)[1].lower()
                    if file_extension in self.default_checked_extensions:
                        item.setCheckState(0, Qt.Checked)
                    else:
                        item.setCheckState(0, Qt.Unchecked)
        except Exception as e:
            print(f"Error loading directory {folderPath}: {e}")
