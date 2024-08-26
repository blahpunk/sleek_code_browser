from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit, 
    QSplitter, QPushButton, QProgressBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from directory_view import DirectoryView

class UiSetup:
    def __init__(self, app):
        self.mainWidget = QWidget()
        app.setCentralWidget(self.mainWidget)
        self.setup_ui()

    def setup_ui(self):
        splitter = QSplitter(Qt.Vertical)

        # Text area and Tabs above the file tree
        contentWidget = QWidget()
        contentLayout = QVBoxLayout(contentWidget)

        # Tab widget for filenames
        self.tabBar = QWidget()
        self.tabLayout = QHBoxLayout(self.tabBar)
        contentLayout.addWidget(self.tabBar)

        self.textArea = QTextEdit()
        self.textArea.setFont(QFont('Consolas', 10))
        self.textArea.setStyleSheet("background-color: #2c2c2c; color: white;")
        contentLayout.addWidget(self.textArea)

        splitter.addWidget(contentWidget)

        # Directory view instead of a plain QTreeWidget
        self.fileTree = DirectoryView()
        splitter.addWidget(self.fileTree)

        splitter.setSizes([400, 200])

        # Progress bar for loading indication
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 0)  # Indeterminate progress bar

        # Buttons layout
        self.buttonsLayout = QHBoxLayout()
        self.selectFolderButton = QPushButton('Select Folder')
        self.showButton = QPushButton('Show')
        self.copyAllButton = QPushButton('Copy All')
        self.buttonsLayout.addWidget(self.selectFolderButton)
        self.buttonsLayout.addWidget(self.showButton)
        self.buttonsLayout.addWidget(self.copyAllButton)

        # Main layout
        mainLayout = QVBoxLayout(self.mainWidget)
        mainLayout.addWidget(splitter)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addLayout(self.buttonsLayout)
