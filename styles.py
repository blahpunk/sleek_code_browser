def apply_styles(app):
    app.setStyleSheet(
        """
        QMainWindow {
            background-color: #181b20;
        }
        QWidget {
            color: #d7dce2;
            font-size: 12px;
        }
        QPushButton {
            background-color: #2b323c;
            color: #e9edf2;
            border: 1px solid #3c4653;
            border-radius: 4px;
            padding: 6px 10px;
        }
        QPushButton:hover {
            background-color: #384351;
        }
        QPushButton:pressed {
            background-color: #23303e;
        }
        QTreeWidget {
            background-color: #1f242c;
            border: 1px solid #2e3642;
            alternate-background-color: #252c36;
        }
        QTreeWidget::item:selected {
            background-color: #365a8c;
            color: #f4f8ff;
        }
        QScrollArea {
            background-color: #1a1f26;
            border: 1px solid #2e3642;
        }
        QScrollBar:horizontal {
            background-color: #1a1f26;
            height: 8px;
        }
        QScrollBar::handle:horizontal {
            background-color: #44515f;
            border-radius: 4px;
            min-width: 20px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
            background: none;
        }
        QPlainTextEdit {
            background-color: #0f141b;
            color: #dce8f3;
            border: 1px solid #2f3a47;
            padding: 8px;
        }
        QLineEdit, QComboBox, QSpinBox {
            background-color: #202833;
            color: #e6edf4;
            border: 1px solid #3a4554;
            border-radius: 4px;
            padding: 4px 6px;
        }
        QComboBox QAbstractItemView {
            background-color: #202833;
            selection-background-color: #365a8c;
            border: 1px solid #3a4554;
        }
        QCheckBox {
            spacing: 6px;
        }
        QLabel {
            color: #c7d1db;
        }
        QGroupBox {
            border: 1px solid #2d3641;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 8px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
        }
        QListWidget {
            background-color: #1b2028;
            border: 1px solid #303946;
        }
        """
    )
