from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QTextEdit,
    QSplitter, QPushButton, QProgressBar, QScrollArea, QFrame
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

        # Top half: text area + tabs
        contentWidget = QWidget()
        contentLayout = QVBoxLayout(contentWidget)

        # Horizontal scrollable area for file tab buttons
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFixedHeight(32)
        self.scrollArea.setStyleSheet("""
            QScrollArea { background-color: #2c2c2c; border: none; }
            QWidget { background-color: #2c2c2c; }
            QScrollBar:horizontal { background-color: #2c2c2c; height: 8px; }
            QScrollBar::handle:horizontal { background-color: #5a5a5a; min-width: 20px; border-radius: 4px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { background: none; width: 0px; }
        """)

        self.tabBar = QWidget()
        self.tabLayout = QHBoxLayout(self.tabBar)
        self.tabLayout.setContentsMargins(0, 0, 0, 0)
        self.tabLayout.setSpacing(5)
        self.scrollArea.setWidget(self.tabBar)

        contentLayout.addWidget(self.scrollArea)

        # Multi-line text editor for file content display
        self.textArea = QTextEdit()
        self.textArea.setFont(QFont('Consolas', 10))
        self.textArea.setStyleSheet("background-color: #2c2c2c; color: #f8f8f8;")
        contentLayout.addWidget(self.textArea)

        splitter.addWidget(contentWidget)

        # Bottom half: tree view of files/folders
        self.fileTree = DirectoryView()
        splitter.addWidget(self.fileTree)
        splitter.setSizes([400, 200])

        # Buttons below the UI
        self.buttonsLayout = QHBoxLayout()
        self.selectFolderButton = QPushButton('Select Folder')
        self.showButton = QPushButton('Show')
        self.copyAllButton = QPushButton('Copy All')
        self.expandSelectedButton = QPushButton('Expand Selected')  # NEW
        self.buttonsLayout.addWidget(self.expandSelectedButton)

        self.refreshButton = QPushButton('Refresh')  # NEW
        self.modifyExclusionsButton = QPushButton('Manage Exclusions')  # NEW

        self.buttonsLayout.addWidget(self.selectFolderButton)
        self.buttonsLayout.addWidget(self.showButton)
        self.buttonsLayout.addWidget(self.copyAllButton)
        self.buttonsLayout.addWidget(self.refreshButton)
        self.buttonsLayout.addWidget(self.modifyExclusionsButton)

        # Main layout of the window
        mainLayout = QVBoxLayout(self.mainWidget)
        mainLayout.addWidget(splitter)
        mainLayout.addLayout(self.buttonsLayout)
