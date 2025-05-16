import os
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import Qt

class DirectoryView(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.folder_path = ""
        self.excluded_extensions = []
        self.excluded_extensions_lower = []
        self.excluded_folders = []
        self.excluded_folders_lower = []
        self.excluded_files = []
        self.excluded_files_lower = []
        self.itemExpanded.connect(self.onItemExpanded)

    def populate(self, folderPath, excluded_extensions=None, excluded_folders=None, excluded_files=None):
        self.clear()
        self.folder_path = folderPath

        self.excluded_extensions = excluded_extensions or []
        self.excluded_extensions_lower = [e.lower() for e in self.excluded_extensions]

        self.excluded_folders = excluded_folders or []
        self.excluded_folders_lower = [f.lower() for f in self.excluded_folders]

        self.excluded_files = excluded_files or []
        self.excluded_files_lower = [f.lower() for f in self.excluded_files]

        self.addDirectoryItems(self.invisibleRootItem(), folderPath, lazy_load=True)

    def addDirectoryItems(self, parentItem, folderPath, lazy_load=False):
        try:
            existing_items = {parentItem.child(i).data(0, Qt.UserRole) for i in range(parentItem.childCount())}

            for fileName in sorted(os.listdir(folderPath)):
                filePath = os.path.join(folderPath, fileName)
                lowerName = fileName.lower()

                if filePath in existing_items:
                    continue

                item = QTreeWidgetItem(parentItem)
                item.setData(0, Qt.UserRole, filePath)

                if os.path.isdir(filePath):
                    item.setText(0, f"📁 {fileName}")
                    if lowerName in self.excluded_folders_lower:
                        item.setCheckState(0, Qt.Unchecked)
                    else:
                        item.setCheckState(0, Qt.Checked)

                    if lazy_load:
                        item.addChild(QTreeWidgetItem(["Loading..."]))
                    else:
                        self.addDirectoryItems(item, filePath, lazy_load=True)
                else:
                    item.setText(0, f"📄 {fileName}")
                    file_extension = os.path.splitext(fileName)[1].lower()

                    if lowerName in self.excluded_files_lower or file_extension in self.excluded_extensions_lower:
                        item.setCheckState(0, Qt.Unchecked)
                    else:
                        item.setCheckState(0, Qt.Checked)
        except Exception as e:
            print(f"Error loading directory {folderPath}: {e}")

    def onItemExpanded(self, item):
        if item.childCount() == 1 and item.child(0).text(0) == "Loading...":
            item.takeChildren()
            folderPath = item.data(0, Qt.UserRole)
            self.addDirectoryItems(item, folderPath, lazy_load=True)

    def get_checked_items(self):
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
                if os.path.isdir(filePath):
                    if not child.isExpanded():
                        self.addDirectoryItems(child, filePath, lazy_load=False)
                    self.collect_checked_items(child, checked_items)

    def refresh(self):
        self.clear()
        if self.folder_path:
            self.populate(
                self.folder_path,
                excluded_extensions=self.excluded_extensions,
                excluded_folders=self.excluded_folders,
                excluded_files=self.excluded_files
            )
