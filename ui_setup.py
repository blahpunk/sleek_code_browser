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

        # Text area and Tabs above the file tree
        contentWidget = QWidget()
        contentLayout = QVBoxLayout(contentWidget)

        # Scroll area for tab buttons
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFixedHeight(32)  # Set height to fit the buttons without extra space
        self.scrollArea.setStyleSheet("""
            QScrollArea {
                background-color: #2c2c2c;  /* Matches the dark theme */
                border: none;
            }
            QWidget {
                background-color: #2c2c2c;  /* Ensures the background behind the buttons is dark */
            }
            QScrollBar:horizontal {
                background-color: #2c2c2c;
                height: 8px;
            }
            QScrollBar::handle:horizontal {
                background-color: #5a5a5a;
                min-width: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
                width: 0px;
            }
        """)

        # Tab widget for filenames inside the scroll area
        self.tabBar = QWidget()
        self.tabLayout = QHBoxLayout(self.tabBar)
        self.tabLayout.setContentsMargins(0, 0, 0, 0)  # No margins
        self.tabLayout.setSpacing(5)  # Adjust spacing as needed
        self.scrollArea.setWidget(self.tabBar)

        contentLayout.addWidget(self.scrollArea)

        self.textArea = QTextEdit()
        self.textArea.setFont(QFont('Consolas', 10))
        self.textArea.setStyleSheet("background-color: #2c2c2c; color: #f8f8f8;")
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

# End of ui_setup.py
