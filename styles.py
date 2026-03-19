from PyQt5.QtWidgets import QApplication

DEFAULT_THEME = "light"

THEMES = {
    "light": {
        "window_bg": "#f4f6f8",
        "panel_bg": "#ffffff",
        "surface_alt": "#eef2f6",
        "surface_deep": "#e8edf3",
        "text": "#1f2933",
        "muted_text": "#5f6f82",
        "border": "#c7d1dc",
        "accent": "#2f6feb",
        "accent_hover": "#245ec9",
        "accent_pressed": "#1d4ea8",
        "selection_bg": "#cfe2ff",
        "selection_text": "#0f1f3a",
        "button_bg": "#f8fafc",
        "button_hover": "#eef3f9",
        "button_pressed": "#e2e9f2",
        "button_disabled_bg": "#edf1f5",
        "button_disabled_text": "#8b98a8",
        "input_bg": "#ffffff",
        "input_border": "#b8c5d4",
        "status_ok": "#3b4c60",
        "status_warning": "#b45309",
        "chip_bg": "#e9f0ff",
        "chip_hover": "#dbe8ff",
        "chip_pressed": "#cadcff",
        "scrollbar_bg": "#e6ecf3",
        "scrollbar_handle": "#9aa8b8",
        "scrollbar_handle_hover": "#7f91a4",
        "scrollbar_handle_pressed": "#65798f",
        "group_title": "#34465a",
        "focus_ring": "#76a5ff",
    },
    "dark": {
        "window_bg": "#181b20",
        "panel_bg": "#1f242c",
        "surface_alt": "#202833",
        "surface_deep": "#0f141b",
        "text": "#d7dce2",
        "muted_text": "#aab6c3",
        "border": "#364150",
        "accent": "#4d88ff",
        "accent_hover": "#3e77ec",
        "accent_pressed": "#2f62cb",
        "selection_bg": "#365a8c",
        "selection_text": "#f4f8ff",
        "button_bg": "#2b323c",
        "button_hover": "#384351",
        "button_pressed": "#23303e",
        "button_disabled_bg": "#232932",
        "button_disabled_text": "#738295",
        "input_bg": "#202833",
        "input_border": "#3a4554",
        "status_ok": "#b8c2cc",
        "status_warning": "#f0b66f",
        "chip_bg": "#2a3650",
        "chip_hover": "#344462",
        "chip_pressed": "#24364e",
        "scrollbar_bg": "#1a1f26",
        "scrollbar_handle": "#44515f",
        "scrollbar_handle_hover": "#526171",
        "scrollbar_handle_pressed": "#3a4755",
        "group_title": "#c7d1db",
        "focus_ring": "#7aa6ff",
    },
}

BASE_QSS = """
QMainWindow, QWidget {{
    background-color: {window_bg};
    color: {text};
    font-size: 12px;
}}
QDialog, QMessageBox, QInputDialog, QFileDialog {{
    background-color: {window_bg};
    color: {text};
}}
QWidget:disabled {{
    color: {button_disabled_text};
}}
QLabel {{
    color: {text};
}}
QLabel#statsLabel {{
    color: {muted_text};
}}
QLabel#statusLabel[statusRole="normal"] {{
    color: {status_ok};
}}
QLabel#statusLabel[statusRole="warning"] {{
    color: {status_warning};
    font-weight: 600;
}}
QLabel#sizeIndicatorLabel {{
    color: {muted_text};
    font-weight: 600;
}}
QPushButton {{
    background-color: {button_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: 5px;
    padding: 6px 10px;
}}
QPushButton:hover {{
    background-color: {button_hover};
}}
QPushButton:pressed {{
    background-color: {button_pressed};
}}
QPushButton:disabled {{
    background-color: {button_disabled_bg};
    color: {button_disabled_text};
}}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{
    background-color: {input_bg};
    color: {text};
    border: 1px solid {input_border};
    border-radius: 4px;
    padding: 4px 6px;
    selection-background-color: {selection_bg};
    selection-color: {selection_text};
}}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {{
    border: 1px solid {focus_ring};
}}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid {input_border};
}}
QComboBox::down-arrow {{
    border: none;
    width: 0px;
    height: 0px;
}}
QComboBox QAbstractItemView {{
    background-color: {panel_bg};
    color: {text};
    border: 1px solid {border};
    selection-background-color: {selection_bg};
    selection-color: {selection_text};
}}
QTreeWidget, QListWidget, QAbstractItemView {{
    background-color: {panel_bg};
    color: {text};
    border: 1px solid {border};
    alternate-background-color: {surface_alt};
    selection-background-color: {selection_bg};
    selection-color: {selection_text};
}}
QTreeWidget::item:selected, QListWidget::item:selected {{
    background-color: {selection_bg};
    color: {selection_text};
}}
QHeaderView::section {{
    background-color: {surface_alt};
    color: {text};
    border: 1px solid {border};
    padding: 4px;
}}
QPlainTextEdit {{
    background-color: {surface_deep};
    padding: 8px;
}}
QScrollArea {{
    background-color: {panel_bg};
    border: 1px solid {border};
}}
QScrollBar:vertical, QScrollBar:horizontal {{
    background-color: {scrollbar_bg};
    border: none;
}}
QScrollBar:vertical {{
    width: 10px;
}}
QScrollBar:horizontal {{
    height: 10px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background-color: {scrollbar_handle};
    border-radius: 5px;
    min-height: 20px;
    min-width: 20px;
}}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
    background-color: {scrollbar_handle_hover};
}}
QScrollBar::handle:vertical:pressed, QScrollBar::handle:horizontal:pressed {{
    background-color: {scrollbar_handle_pressed};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    width: 0px;
    height: 0px;
    background: none;
    border: none;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: transparent;
}}
QGroupBox {{
    border: 1px solid {border};
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    color: {group_title};
    padding: 0 4px;
}}
QCheckBox {{
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid {border};
    border-radius: 3px;
    background-color: {panel_bg};
}}
QCheckBox::indicator:checked {{
    background-color: {accent};
    border: 1px solid {accent};
}}
QSplitter::handle {{
    background-color: {border};
}}
QSplitter::handle:vertical {{
    height: 2px;
}}
QToolTip {{
    background-color: {panel_bg};
    color: {text};
    border: 1px solid {border};
    padding: 4px;
}}
"""


def normalize_theme(theme_name):
    normalized = str(theme_name or "").strip().lower()
    if normalized in THEMES:
        return normalized
    return DEFAULT_THEME


def get_stylesheet(theme_name):
    theme_key = normalize_theme(theme_name)
    return BASE_QSS.format(**THEMES[theme_key])


def apply_theme(target, theme_name):
    selected_theme = normalize_theme(theme_name)
    stylesheet = get_stylesheet(selected_theme)

    app = target if isinstance(target, QApplication) else QApplication.instance()
    if app is not None:
        app.setStyleSheet(stylesheet)
    elif target is not None:
        target.setStyleSheet(stylesheet)

    return selected_theme


def apply_styles(target):
    return apply_theme(target, DEFAULT_THEME)
