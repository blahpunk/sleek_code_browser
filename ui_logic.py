import os
import mimetypes
import configparser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog, QPushButton, QToolButton, QApplication,
    QDialog, QVBoxLayout, QLabel, QListWidget, QHBoxLayout,
    QInputDialog, QMessageBox
)
from PyQt5.QtGui import QColor

class UiLogic:
    def __init__(self, ui_setup):
        self.ui_setup = ui_setup
        self.filePositions = {}
        self.excluded_extensions = []
        self.excluded_folders = []
        self.excluded_files = []
        self.load_exclusions()
        self.connect_signals()

    def load_exclusions(self):
        config_path = 'settings.ini'

        # If the file doesn't exist, create it with default values
        if not os.path.exists(config_path):
            default_ini = """[Extensions]
    excluded = .exe, .bin, .dll, .obj, .ico, .ini, .md, .jpg, .gif, .png, .mkv, .mp4

    [Exclusions]
    folders = __pycache__, build, .git, node_modules, dist
    files = thumbs.db, desktop.ini, .gitignore
    """
            with open(config_path, 'w') as f:
                f.write(default_ini)

        # Now load it
        config = configparser.ConfigParser()
        config.read(config_path)

        try:
            ext = config.get('Extensions', 'excluded', fallback='')
            self.excluded_extensions = [x.strip() for x in ext.split(',') if x.strip()]
        except Exception as e:
            print(f"Failed to load excluded extensions: {e}")
            self.excluded_extensions = []

        try:
            folders = config.get('Exclusions', 'folders', fallback='')
            self.excluded_folders = [x.strip() for x in folders.split(',') if x.strip()]
        except Exception as e:
            print(f"Failed to load excluded folders: {e}")
            self.excluded_folders = []

        try:
            files = config.get('Exclusions', 'files', fallback='')
            self.excluded_files = [x.strip() for x in files.split(',') if x.strip()]
        except Exception as e:
            print(f"Failed to load excluded files: {e}")
            self.excluded_files = []


    def connect_signals(self):
        self.ui_setup.selectFolderButton.clicked.connect(self.selectFolder)
        self.ui_setup.showButton.clicked.connect(self.showContents)
        self.ui_setup.copyAllButton.clicked.connect(self.copyAllText)
        self.ui_setup.refreshButton.clicked.connect(self.refreshFolder)
        self.ui_setup.modifyExclusionsButton.clicked.connect(self.manageExclusions)

    def selectFolder(self):
        folderPath = QFileDialog.getExistingDirectory(self.ui_setup.mainWidget, "Select Folder")
        if folderPath:
            folderPath = os.path.abspath(folderPath)
            self.populateFileTree(folderPath)
            self.updateWindowTitle(folderPath)

    def refreshFolder(self):
        if not self.ui_setup.fileTree.folder_path:
            return
        self.load_exclusions()
        self.populateFileTree(self.ui_setup.fileTree.folder_path)

    def populateFileTree(self, folderPath):
        self.ui_setup.fileTree.clear()
        self.ui_setup.fileTree.populate(
            folderPath,
            excluded_extensions=self.excluded_extensions,
            excluded_folders=self.excluded_folders,
            excluded_files=self.excluded_files
        )

    def updateWindowTitle(self, folderPath):
        folderName = os.path.basename(folderPath)
        self.ui_setup.mainWidget.window().setWindowTitle(f"Sleek Code Browser - {folderName}")

    def showContents(self):
        self.ui_setup.textArea.clear()
        self.clearTabs()
        self.filePositions.clear()
        checked_items = self.ui_setup.fileTree.get_checked_items()
        added_files = set()

        for filePath in checked_items:
            if os.path.isfile(filePath) and filePath not in added_files:
                self.displayFileContent(filePath)
                added_files.add(filePath)

    def clearTabs(self):
        while self.ui_setup.tabLayout.count():
            child = self.ui_setup.tabLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def is_text_file(self, filePath):
        mime_type, _ = mimetypes.guess_type(filePath)
        return mime_type and mime_type.startswith('text')

    def displayFileContent(self, filePath):
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                content = file.read()
                relativePath = os.path.relpath(filePath, self.ui_setup.fileTree.folder_path)

                cursor_pos = self.ui_setup.textArea.textCursor().position()
                self.filePositions[filePath] = cursor_pos

                self.ui_setup.textArea.setTextColor(QColor('green'))
                self.ui_setup.textArea.insertPlainText(f"# {relativePath}\n")
                self.insertColoredLine('green')

                self.ui_setup.textArea.setTextColor(QColor('white'))
                self.ui_setup.textArea.insertPlainText(content)

                self.insertColoredLine('red')
                self.ui_setup.textArea.setTextColor(QColor('red'))
                self.ui_setup.textArea.insertPlainText(f"\n# End of {os.path.basename(filePath)}\n")

                tabButton = QPushButton(os.path.basename(filePath))
                tabButton.clicked.connect(lambda checked, pos=cursor_pos: self.scrollToPosition(pos))
                self.ui_setup.tabLayout.addWidget(tabButton)

                copyButton = QToolButton()
                copyButton.setText("📋")
                copyButton.clicked.connect(lambda checked, path=filePath: self.copyFileContent(path))
                self.ui_setup.tabLayout.addWidget(copyButton)

        except Exception as e:
            self.ui_setup.textArea.append(f"Error reading {filePath}: {str(e)}")

    def insertColoredLine(self, color):
        cursor = self.ui_setup.textArea.textCursor()
        cursor.insertHtml(f'<hr style="background-color:{color}; height:3px; border:none;">')

    def scrollToPosition(self, position):
        cursor = self.ui_setup.textArea.textCursor()
        cursor.setPosition(position)
        self.ui_setup.textArea.setTextCursor(cursor)
        self.ui_setup.textArea.ensureCursorVisible()

    def copyFileContent(self, filePath):
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                relativePath = os.path.relpath(filePath, self.ui_setup.fileTree.folder_path)
                content = file.read()
                fullContent = f"# {relativePath}\n{content}\n# End of {os.path.basename(filePath)}\n"
                clipboard = QApplication.clipboard()
                clipboard.setText(fullContent)
        except Exception as e:
            self.ui_setup.textArea.append(f"Error copying {filePath}: {str(e)}")

    def copyAllText(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.ui_setup.textArea.toPlainText())

    def manageExclusions(self):
        self.load_exclusions()  # Ensure settings.ini is re-read fresh
        dialog = QDialog(self.ui_setup.mainWidget)
        dialog.setWindowTitle("Manage Exclusions")
        layout = QVBoxLayout(dialog)

        sections = [
            ("Extensions", self.excluded_extensions),
            ("Folders", self.excluded_folders),
            ("Files", self.excluded_files)
        ]
        widgets = []

        for label_text, items in sections:
            layout.addWidget(QLabel(label_text))
            list_widget = QListWidget()
            list_widget.addItems(items)
            widgets.append((label_text.lower(), list_widget))
            layout.addWidget(list_widget)

            btn_layout = QHBoxLayout()
            add_btn = QPushButton("Add")
            remove_btn = QPushButton("Remove")
            btn_layout.addWidget(add_btn)
            btn_layout.addWidget(remove_btn)

            def make_add_fn(lst):
                def add():
                    text, ok = QInputDialog.getText(dialog, "Add Item", "Enter new exclusion:")
                    if ok and text.strip():
                        lst.addItem(text.strip().lower())
                return add

            def make_remove_fn(lst):
                def remove():
                    for item in lst.selectedItems():
                        lst.takeItem(lst.row(item))
                return remove

            add_btn.clicked.connect(make_add_fn(list_widget))
            remove_btn.clicked.connect(make_remove_fn(list_widget))
            layout.addLayout(btn_layout)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(lambda: self.saveExclusionsAndClose(widgets, dialog))
        layout.addWidget(ok_button)

        dialog.exec_()

    def saveExclusionsAndClose(self, widgets, dialog):
        config = configparser.ConfigParser()
        config.read('settings.ini')

        # Preserve original case, but still normalize extensions with leading dot
        ext_list = []
        for i in range(widgets[0][1].count()):
            ext = widgets[0][1].item(i).text().strip()
            if not ext.startswith('.'):
                ext = '.' + ext
            ext_list.append(ext)

        # Preserve case for folders and files
        folders_list = [widgets[1][1].item(i).text().strip() for i in range(widgets[1][1].count())]
        files_list = [widgets[2][1].item(i).text().strip() for i in range(widgets[2][1].count())]

        config.set('Extensions', 'excluded', ', '.join(ext_list))
        config.set('Exclusions', 'folders', ', '.join(folders_list))
        config.set('Exclusions', 'files', ', '.join(files_list))

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

        self.load_exclusions()
        if self.ui_setup.fileTree.folder_path:
            self.populateFileTree(self.ui_setup.fileTree.folder_path)

        dialog.accept()
