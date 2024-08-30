import os
import mimetypes
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QPushButton, QToolButton, QApplication
from PyQt5.QtGui import QColor

class UiLogic:
    def __init__(self, ui_setup):
        self.ui_setup = ui_setup
        self.filePositions = {}  # Store the position of each file in the text area
        self.default_checked_extensions = [
            '.py', '.txt', '.log', '.md', '.json', '.xml', '.ini', '.sh', '.bat', '.pl', '.rb', '.php', '.html', '.css', '.js', '.yml', '.yaml'
        ]  # List of extensions to be checked by default
        self.connect_signals()

    def connect_signals(self):
        self.ui_setup.selectFolderButton.clicked.connect(self.selectFolder)
        self.ui_setup.showButton.clicked.connect(self.showContents)
        self.ui_setup.copyAllButton.clicked.connect(self.copyAllText)

    def selectFolder(self):
        folderPath = QFileDialog.getExistingDirectory(self.ui_setup.mainWidget, "Select Folder")
        if folderPath:
            folderPath = os.path.abspath(folderPath)  # Ensure the selected path is absolute
            self.populateFileTree(folderPath)

    def populateFileTree(self, folderPath):
        self.ui_setup.fileTree.clear()  # Clear the tree to avoid duplication
        self.ui_setup.fileTree.populate(folderPath, self.default_checked_extensions)  # Populate the tree

    def showContents(self):
        self.ui_setup.textArea.clear()  # Clear the text area
        self.clearTabs()  # Clear the tab buttons before adding new ones
        self.filePositions.clear()  # Clear stored file positions

        checked_items = self.ui_setup.fileTree.get_checked_items()
        added_files = set()  # Set to keep track of already added files

        for filePath in checked_items:
            if os.path.isfile(filePath) and filePath not in added_files:
                self.displayFileContent(filePath)
                added_files.add(filePath)  # Add filePath to the set after it's displayed

    def clearTabs(self):
        """Clear all tabs and buttons from the layout."""
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

                # Store the cursor position before appending the content
                cursor_pos = self.ui_setup.textArea.textCursor().position()
                self.filePositions[filePath] = cursor_pos

                # Insert the green line before the file content
                self.ui_setup.textArea.setTextColor(QColor('green'))
                self.ui_setup.textArea.insertPlainText(f"# {relativePath}\n")
                self.insertColoredLine('green')

                # Insert the file content
                self.ui_setup.textArea.setTextColor(QColor('white'))
                self.ui_setup.textArea.insertPlainText(content)

                # Insert the red line after the file content
                self.insertColoredLine('red')
                self.ui_setup.textArea.setTextColor(QColor('red'))
                self.ui_setup.textArea.insertPlainText(f"\n# End of {os.path.basename(filePath)}\n")

                # Add a tab button to jump to the file content
                tabButton = QPushButton(os.path.basename(filePath))
                tabButton.clicked.connect(lambda checked, pos=cursor_pos: self.scrollToPosition(pos))
                self.ui_setup.tabLayout.addWidget(tabButton)

                # Add a copy button to copy the file content to clipboard
                copyButton = QToolButton()
                copyButton.setText("📋")
                copyButton.clicked.connect(lambda checked, path=filePath: self.copyFileContent(path))
                self.ui_setup.tabLayout.addWidget(copyButton)

        except Exception as e:
            self.ui_setup.textArea.append(f"Error reading {filePath}: {str(e)}")

    def insertColoredLine(self, color):
        """Inserts a solid colored line in the text area"""
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

# End of ui_logic.py
