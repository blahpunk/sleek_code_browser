from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from directory_view import DirectoryView


class UiSetup:
    def __init__(self, app):
        self.mainWidget = QWidget()
        app.setCentralWidget(self.mainWidget)
        self.setup_ui()

    def setup_ui(self):
        self.mainLayout = QVBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(8, 8, 8, 8)
        self.mainLayout.setSpacing(8)

        self.splitter = QSplitter(Qt.Vertical)

        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(6)

        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(8)

        self.bundleModeLabel = QLabel("Bundle Mode")
        self.bundleModeCombo = QComboBox()
        self.bundleModeCombo.addItem("AI Bundle Mode", "ai_bundle")
        self.bundleModeCombo.addItem("Language-Safe Mode", "language_safe")

        self.includeEndMarkersCheck = QCheckBox("Include end markers")
        self.themeLabel = QLabel("Theme")
        self.themeCombo = QComboBox()
        self.themeCombo.addItem("Light", "light")
        self.themeCombo.addItem("Dark", "dark")

        self.sizeIndicatorTitleLabel = QLabel("Size Indicator")
        self.sizeIndicatorLabel = QLabel("Ready")
        self.sizeIndicatorLabel.setObjectName("sizeIndicatorLabel")

        options_layout.addWidget(self.bundleModeLabel)
        options_layout.addWidget(self.bundleModeCombo)
        options_layout.addWidget(self.includeEndMarkersCheck)
        options_layout.addWidget(self.themeLabel)
        options_layout.addWidget(self.themeCombo)
        options_layout.addStretch(1)
        options_layout.addWidget(self.sizeIndicatorTitleLabel)
        options_layout.addWidget(self.sizeIndicatorLabel)
        top_layout.addLayout(options_layout)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setFixedHeight(34)

        self.tabBar = QWidget()
        self.tabLayout = QHBoxLayout(self.tabBar)
        self.tabLayout.setContentsMargins(0, 0, 0, 0)
        self.tabLayout.setSpacing(4)
        self.scrollArea.setWidget(self.tabBar)
        top_layout.addWidget(self.scrollArea)

        self.textArea = QPlainTextEdit()
        self.textArea.setReadOnly(True)
        self.textArea.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.textArea.setFont(QFont("Consolas", 10))
        top_layout.addWidget(self.textArea)

        info_layout = QHBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        self.statsLabel = QLabel("0 files | 0 chars | 0 bytes | 0 lines | ~0 tokens")
        self.statsLabel.setObjectName("statsLabel")
        self.statusLabel = QLabel("Select a folder to begin.")
        self.statusLabel.setObjectName("statusLabel")
        self.statusLabel.setProperty("statusRole", "normal")
        info_layout.addWidget(self.statsLabel, 1)
        info_layout.addWidget(self.statusLabel, 1)
        top_layout.addLayout(info_layout)

        self.splitter.addWidget(top_widget)

        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(6)

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(8)
        self.nameFilterInput = QLineEdit()
        self.nameFilterInput.setPlaceholderText("Filter name (substring)")
        self.extensionFilterInput = QLineEdit()
        self.extensionFilterInput.setPlaceholderText("Extension filter (e.g. .py)")
        self.showCheckedOnlyCheck = QCheckBox("Show checked only")
        filter_layout.addWidget(self.nameFilterInput, 2)
        filter_layout.addWidget(self.extensionFilterInput, 1)
        filter_layout.addWidget(self.showCheckedOnlyCheck)
        tree_layout.addLayout(filter_layout)

        self.fileTree = DirectoryView()
        tree_layout.addWidget(self.fileTree)
        self.splitter.addWidget(tree_widget)
        self.splitter.setSizes([450, 260])

        self.mainLayout.addWidget(self.splitter, 1)

        self.buttonsLayout = QHBoxLayout()
        self.buttonsLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonsLayout.setSpacing(8)

        self.selectFolderButton = QPushButton("Select Folder")
        self.refreshButton = QPushButton("Refresh")
        self.expandCheckedButton = QPushButton("Expand Checked")
        self.buildBundleButton = QPushButton("Build Bundle")
        self.copyBundleButton = QPushButton("Copy Bundle")
        self.exportBundleButton = QPushButton("Export TXT")
        self.manageExclusionsButton = QPushButton("Manage Exclusions")
        self.windowsIntegrationButton = QPushButton("Repair Windows Integration")

        self.buttonsLayout.addWidget(self.selectFolderButton)
        self.buttonsLayout.addWidget(self.refreshButton)
        self.buttonsLayout.addWidget(self.expandCheckedButton)
        self.buttonsLayout.addWidget(self.buildBundleButton)
        self.buttonsLayout.addWidget(self.copyBundleButton)
        self.buttonsLayout.addWidget(self.exportBundleButton)
        self.buttonsLayout.addWidget(self.manageExclusionsButton)
        self.buttonsLayout.addWidget(self.windowsIntegrationButton)
        self.mainLayout.addLayout(self.buttonsLayout)
