# directory_view.py

import os
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

class DirectoryView(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)  # Hide the header for a cleaner look
        self.folder_path = ""  # Initialize the folder path attribute
        self.default_checked_extensions = []

        # Connect the item expanded signal to load items lazily
        self.itemExpanded.connect(self.onItemExpanded)

    def populate(self, folderPath, default_checked_extensions=None):
        self.clear()  # Clear existing items
        self.folder_path = folderPath  # Store the folder path
        self.default_checked_extensions = default_checked_extensions if default_checked_extensions else []  # Store the default checked extensions
        self.addDirectoryItems(self.invisibleRootItem(), folderPath, lazy_load=True)

    def addDirectoryItems(self, parentItem, folderPath, lazy_load=False):
        try:
            for fileName in sorted(os.listdir(folderPath)):
                filePath = os.path.join(folderPath, fileName)
                item = QTreeWidgetItem(parentItem)
                item.setData(0, Qt.UserRole, filePath)  # Store the file path in the item

                if os.path.isdir(filePath):
                    item.setText(0, f"📁 {fileName}")
                    item.setCheckState(0, Qt.Checked)  # Folders are always checked by default

                    if lazy_load:
                        # Use a placeholder child to indicate the folder can be expanded
                        item.addChild(QTreeWidgetItem(["Loading..."]))
                    else:
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

    def onItemExpanded(self, item):
        # Load the contents of the directory when expanded
        if item.childCount() == 1 and item.child(0).text(0) == "Loading...":
            item.takeChildren()  # Remove the placeholder
            folderPath = item.data(0, Qt.UserRole)
            self.addDirectoryItems(item, folderPath)  # Load the actual contents

# End of directory_view.py
