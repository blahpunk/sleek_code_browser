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
            existing_items = set()  # Track added items to prevent duplicates

            for i in range(parentItem.childCount()):
                child = parentItem.child(i)
                existing_items.add(child.text(0))

            for fileName in sorted(os.listdir(folderPath)):
                if fileName in existing_items:
                    continue

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
                        self.addDirectoryItems(item, filePath, lazy_load=True)  # Recursively add subdirectories

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
            self.addDirectoryItems(item, folderPath, lazy_load=True)  # Load the actual contents

    def get_checked_items(self):
        """Recursively collect all checked files and folders."""
        checked_items = []
        self.collect_checked_items(self.invisibleRootItem(), checked_items)
        return checked_items

    def collect_checked_items(self, parentItem, checked_items):
        for i in range(parentItem.childCount()):
            child = parentItem.child(i)
            filePath = child.data(0, Qt.UserRole)

            if child.checkState(0) == Qt.Checked:
                if filePath:
                    checked_items.append(filePath)

                # If this is a directory, recurse into it
                if os.path.isdir(filePath):
                    # Ensure all items in this directory are checked
                    if not child.isExpanded():
                        # Manually expand the directory to ensure all items are included
                        self.addDirectoryItems(child, filePath, lazy_load=False)
                    self.collect_checked_items(child, checked_items)

# End of directory_view.py
