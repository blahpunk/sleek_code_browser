def apply_styles(app):
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1c1c1c;
        }
        QPushButton {
            background-color: #3a3a3a;
            color: #ffffff;
            border: 1px solid #444444;
            padding: 5px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        QTreeWidget {
            background-color: #262626;
            color: white;
            alternate-background-color: #333333;
            border: none;
        }
        QTabBar::tab {
            background-color: #3a3a3a;
            color: #ffffff;
            border: 1px solid #444444;
            padding: 5px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        QTabBar::tab:selected {
            background-color: #5a5a5a;
        }
        QTextEdit {
            background-color: #1e1e1e;
            color: #f8f8f8;
            border: none;
            padding: 10px;
        }
        QProgressBar {
            background-color: #3a3a3a;
            color: #ffffff;
            border-radius: 5px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #6aa84f;
            width: 20px;
        }
    """)
