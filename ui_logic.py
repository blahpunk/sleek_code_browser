import configparser
import copy
import ctypes
import json
import math
import os
import re
import sys
from datetime import datetime

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from styles import DEFAULT_THEME, apply_theme, normalize_theme

if os.name == "nt":
    import winreg


SOFT_TOKEN_WARNING = 12000
HARD_TOKEN_WARNING = 24000


EXCLUSION_MODULES = {
    "dependency_folders": {
        "label": "Exclude dependency folders",
        "folders": [
            "node_modules",
            "vendor",
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            ".next",
            ".nuxt",
            ".svelte-kit",
            ".turbo",
            ".parcel-cache",
            ".yarn",
            ".npm",
            ".pnpm-store",
            "bower_components",
            "jspm_packages",
            ".gradle",
            ".ruff_cache",
            ".hypothesis",
            ".nox",
            "target",
            "bin",
            "obj",
            "dist",
            "build",
            "out",
            ".output",
        ],
    },
    "build_artifacts": {
        "label": "Exclude build artifacts",
        "folders": [
            "dist",
            "build",
            "out",
            "coverage",
            ".cache",
            ".sass-cache",
            ".nyc_output",
            ".pytest_cache",
            ".vite",
            ".webpack",
            ".rollup.cache",
            "tmp",
            "temp",
            "release",
            "debug",
        ],
        "extensions": [
            ".pyc",
            ".pyo",
            ".class",
            ".o",
            ".obj",
            ".so",
            ".dll",
            ".exe",
            ".dylib",
            ".a",
            ".lib",
            ".pdb",
            ".idb",
            ".ilk",
            ".exp",
            ".wasm",
        ],
    },
    "media_binary_assets": {
        "label": "Exclude media/binary assets",
        "extensions": [
            ".png",
            ".jpg",
            ".jpeg",
            ".jfif",
            ".pjpeg",
            ".pjp",
            ".gif",
            ".apng",
            ".webp",
            ".avif",
            ".heic",
            ".heif",
            ".bmp",
            ".ico",
            ".icns",
            ".tiff",
            ".tif",
            ".svg",
            ".psd",
            ".ai",
            ".raw",
            ".cr2",
            ".nef",
            ".arw",
            ".dng",
            ".mp3",
            ".wav",
            ".ogg",
            ".opus",
            ".aac",
            ".flac",
            ".m4a",
            ".mp4",
            ".m4v",
            ".mkv",
            ".avi",
            ".mov",
            ".mpeg",
            ".mpg",
            ".3gp",
            ".ts",
            ".flv",
            ".wmv",
            ".webm",
            ".zip",
            ".7z",
            ".rar",
            ".tar",
            ".gz",
            ".bz2",
            ".xz",
            ".zst",
            ".lz4",
            ".iso",
            ".dmg",
            ".cab",
            ".ttf",
            ".otf",
            ".woff",
            ".woff2",
            ".pdf",
            ".doc",
            ".docx",
            ".ppt",
            ".pptx",
            ".xls",
            ".xlsx",
            ".sqlite",
            ".sqlite3",
            ".db",
            ".bin",
            ".dat",
        ],
    },
    "logs_cache": {
        "label": "Exclude logs/cache",
        "folders": [".cache", "tmp", "temp", "logs"],
        "files": ["npm-debug.log", "yarn-error.log", "pnpm-debug.log", "lerna-debug.log", ".eslintcache"],
        "extensions": [".log", ".pid", ".tmp", ".bak", ".swp", ".cache", ".dmp", ".stackdump"],
    },
    "editor_vcs_noise": {
        "label": "Exclude editor/VCS noise",
        "folders": [".git", ".svn", ".hg", ".idea", ".vs", ".vscode", ".history", ".fleet", ".settings"],
        "files": [".gitignore", ".gitattributes", ".gitmodules", "thumbs.db", "desktop.ini", ".ds_store"],
    },
    "sensitive_files": {
        "label": "Exclude sensitive files",
        "files": [
            ".env",
            ".env.local",
            ".env.test",
            ".env.development",
            ".env.production",
            "secrets.json",
            "credentials.json",
            "id_rsa",
            "id_ed25519",
            ".htpasswd",
            ".netrc",
        ],
        "extensions": [".pem", ".key", ".pfx", ".p12", ".crt", ".cer", ".jks", ".keystore"],
    },
    "docs_markdown": {
        "label": "Exclude docs/markdown",
        "folders": ["docs", "documentation", "screenshots"],
        "extensions": [".md", ".rst", ".txt", ".adoc"],
    },
    "lockfiles": {
        "label": "Exclude lockfiles",
        "files": [
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "bun.lockb",
            "composer.lock",
            "poetry.lock",
            "cargo.lock",
            "pipfile.lock",
            "gemfile.lock",
        ],
        "extensions": [".lock"],
    },
    "test_reports": {
        "label": "Exclude test snapshots/reports",
        "folders": ["coverage", "__snapshots__", "reports"],
        "extensions": [".snap"],
    },
}

MODULE_ORDER = [
    "dependency_folders",
    "build_artifacts",
    "media_binary_assets",
    "logs_cache",
    "editor_vcs_noise",
    "sensitive_files",
    "docs_markdown",
    "lockfiles",
    "test_reports",
]

PRESET_DEFINITIONS = {
    "minimal_safe": {
        "label": "Minimal Safe",
        "modules": ["editor_vcs_noise", "sensitive_files", "media_binary_assets"],
    },
    "standard_code_project": {
        "label": "Standard Code Project",
        "modules": [
            "dependency_folders",
            "build_artifacts",
            "media_binary_assets",
            "logs_cache",
            "editor_vcs_noise",
            "sensitive_files",
        ],
    },
    "source_only": {
        "label": "Source Only",
        "modules": [
            "dependency_folders",
            "build_artifacts",
            "media_binary_assets",
            "logs_cache",
            "editor_vcs_noise",
            "sensitive_files",
            "docs_markdown",
            "lockfiles",
            "test_reports",
        ],
    },
    "full_project_review": {
        "label": "Full Project Review",
        "modules": ["dependency_folders", "editor_vcs_noise", "sensitive_files"],
    },
    "frontend_web_app": {
        "label": "Frontend Web App",
        "modules": [
            "dependency_folders",
            "build_artifacts",
            "logs_cache",
            "editor_vcs_noise",
            "sensitive_files",
        ],
    },
    "python_project": {
        "label": "Python Project",
        "modules": [
            "dependency_folders",
            "build_artifacts",
            "logs_cache",
            "editor_vcs_noise",
            "sensitive_files",
        ],
    },
    "php_web_server_project": {
        "label": "PHP / Web Server Project",
        "modules": [
            "dependency_folders",
            "build_artifacts",
            "logs_cache",
            "editor_vcs_noise",
            "sensitive_files",
        ],
    },
    "node_tooling_full_stack": {
        "label": "Node Tooling / Full Stack",
        "modules": [
            "dependency_folders",
            "build_artifacts",
            "logs_cache",
            "editor_vcs_noise",
            "sensitive_files",
        ],
    },
}

PRESET_ORDER = [
    "minimal_safe",
    "standard_code_project",
    "source_only",
    "full_project_review",
    "frontend_web_app",
    "python_project",
    "php_web_server_project",
    "node_tooling_full_stack",
]

HASH_STYLE_EXTENSIONS = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".toml",
    ".properties",
    ".ps1",
    ".rb",
    ".r",
    ".pl",
}

SLASH_STYLE_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".php",
    ".swift",
    ".kt",
    ".kts",
    ".rs",
}

SQL_STYLE_EXTENSIONS = {".sql"}
REM_STYLE_EXTENSIONS = {".bat", ".cmd"}
CSS_STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
HTML_STYLE_EXTENSIONS = {".html", ".htm", ".xml", ".svg"}


class ListEditor(QWidget):
    def __init__(self, title, values=None, is_extension_list=False, parent=None):
        super().__init__(parent)
        self.is_extension_list = is_extension_list
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

        self.titleLabel = QLabel(title)
        self.listWidget = QListWidget()
        self.listWidget.setMinimumHeight(120)
        self.layout.addWidget(self.titleLabel)
        self.layout.addWidget(self.listWidget, 1)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(4)
        self.addButton = QPushButton("Add")
        self.removeButton = QPushButton("Remove")
        button_row.addWidget(self.addButton)
        button_row.addWidget(self.removeButton)
        self.layout.addLayout(button_row)

        self.addButton.clicked.connect(self._add_item)
        self.removeButton.clicked.connect(self._remove_selected_items)
        self.set_values(values or [])

    def _normalize_item(self, text):
        normalized = text.strip().lower()
        if not normalized:
            return ""
        if self.is_extension_list and not normalized.startswith("."):
            normalized = f".{normalized}"
        return normalized

    def _add_item(self):
        value, ok = QInputDialog.getText(self, "Add Value", "Enter value:")
        if not ok:
            return
        normalized = self._normalize_item(value)
        if not normalized:
            return
        existing = set(self.values())
        if normalized in existing:
            return
        self.listWidget.addItem(normalized)
        self._sort_items()

    def _remove_selected_items(self):
        for item in self.listWidget.selectedItems():
            self.listWidget.takeItem(self.listWidget.row(item))

    def _sort_items(self):
        items = self.values()
        self.set_values(items)

    def set_values(self, values):
        self.listWidget.clear()
        for value in sorted({self._normalize_item(v) for v in values if self._normalize_item(v)}):
            self.listWidget.addItem(value)

    def values(self):
        return [self.listWidget.item(index).text().strip() for index in range(self.listWidget.count())]


class ExclusionsDialog(QDialog):
    def __init__(
        self,
        initial_config,
        current_folder="",
        has_project_override=False,
        auto_detected_preset=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Manage Exclusions")
        self.resize(980, 700)
        self.clear_override_requested = False
        self._auto_detected_preset = auto_detected_preset if auto_detected_preset in PRESET_DEFINITIONS else None
        self._initializing = True

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        scope_row = QHBoxLayout()
        scope_row.setContentsMargins(0, 0, 0, 0)
        self.scopeLabel = QLabel("Save scope")
        self.scopeCombo = QComboBox()
        self.scopeCombo.addItem("Global defaults", "global")
        if current_folder:
            folder_name = os.path.basename(current_folder) or current_folder
            self.scopeCombo.addItem(f"This project only ({folder_name})", "project")
            if has_project_override:
                self.scopeCombo.setCurrentIndex(1)
        scope_row.addWidget(self.scopeLabel)
        scope_row.addWidget(self.scopeCombo)
        scope_row.addStretch(1)
        main_layout.addLayout(scope_row)

        preset_row = QHBoxLayout()
        preset_row.setContentsMargins(0, 0, 0, 0)
        preset_row.setSpacing(8)
        self.presetLabel = QLabel("Preset")
        self.presetCombo = QComboBox()
        for preset_id in PRESET_ORDER:
            self.presetCombo.addItem(PRESET_DEFINITIONS[preset_id]["label"], preset_id)
        preset_row.addWidget(self.presetLabel)
        preset_row.addWidget(self.presetCombo)

        self.autoDetectButton = QPushButton("Use Detected Preset")
        self.autoDetectButton.setEnabled(bool(self._auto_detected_preset))
        preset_row.addWidget(self.autoDetectButton)
        preset_row.addStretch(1)
        main_layout.addLayout(preset_row)

        modules_group = QGroupBox("Toggleable Exclusion Sets")
        modules_layout = QGridLayout(modules_group)
        modules_layout.setContentsMargins(8, 12, 8, 8)
        modules_layout.setSpacing(6)
        self.module_checks = {}
        for index, module_id in enumerate(MODULE_ORDER):
            checkbox = QCheckBox(EXCLUSION_MODULES[module_id]["label"])
            self.module_checks[module_id] = checkbox
            row = index // 2
            col = index % 2
            modules_layout.addWidget(checkbox, row, col)
        main_layout.addWidget(modules_group)

        custom_group = QGroupBox("Custom Exclusions")
        custom_layout = QHBoxLayout(custom_group)
        custom_layout.setContentsMargins(8, 12, 8, 8)
        custom_layout.setSpacing(8)
        self.customFoldersEditor = ListEditor("Folders", initial_config.get("custom_excluded_folders", []))
        self.customFilesEditor = ListEditor("Files", initial_config.get("custom_excluded_files", []))
        self.customExtensionsEditor = ListEditor(
            "Extensions",
            initial_config.get("custom_excluded_extensions", []),
            is_extension_list=True,
        )
        custom_layout.addWidget(self.customFoldersEditor, 1)
        custom_layout.addWidget(self.customFilesEditor, 1)
        custom_layout.addWidget(self.customExtensionsEditor, 1)
        main_layout.addWidget(custom_group, 1)

        include_group = QGroupBox("Always Include Overrides")
        include_layout = QHBoxLayout(include_group)
        include_layout.setContentsMargins(8, 12, 8, 8)
        include_layout.setSpacing(8)
        self.includeFoldersEditor = ListEditor("Folders", initial_config.get("always_include_folders", []))
        self.includeFilesEditor = ListEditor("Files", initial_config.get("always_include_files", []))
        self.includeExtensionsEditor = ListEditor(
            "Extensions",
            initial_config.get("always_include_extensions", []),
            is_extension_list=True,
        )
        include_layout.addWidget(self.includeFoldersEditor, 1)
        include_layout.addWidget(self.includeFilesEditor, 1)
        include_layout.addWidget(self.includeExtensionsEditor, 1)
        main_layout.addWidget(include_group, 1)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if current_folder:
            self.clearProjectOverrideButton = QPushButton("Clear Project Override")
            self.clearProjectOverrideButton.setEnabled(has_project_override)
            self.clearProjectOverrideButton.clicked.connect(self._clear_project_override)
            self.buttonBox.addButton(self.clearProjectOverrideButton, QDialogButtonBox.ActionRole)

        main_layout.addWidget(self.buttonBox)

        self._set_config(initial_config)
        self.presetCombo.currentIndexChanged.connect(self._preset_changed)
        self.autoDetectButton.clicked.connect(self._use_detected_preset)
        self._initializing = False

    def _set_config(self, config):
        preset_id = config.get("preset_id", "standard_code_project")
        preset_index = self.presetCombo.findData(preset_id)
        if preset_index < 0:
            preset_index = self.presetCombo.findData("standard_code_project")
        self.presetCombo.setCurrentIndex(preset_index)

        enabled_modules = set(config.get("enabled_modules") or [])
        for module_id, checkbox in self.module_checks.items():
            checkbox.setChecked(module_id in enabled_modules)

    def _preset_changed(self):
        if self._initializing:
            return
        preset_id = self.presetCombo.currentData()
        default_modules = set(PRESET_DEFINITIONS[preset_id]["modules"])
        for module_id, checkbox in self.module_checks.items():
            checkbox.setChecked(module_id in default_modules)

    def _use_detected_preset(self):
        if not self._auto_detected_preset:
            return
        index = self.presetCombo.findData(self._auto_detected_preset)
        if index >= 0:
            self.presetCombo.setCurrentIndex(index)

    def _clear_project_override(self):
        answer = QMessageBox.question(
            self,
            "Clear Project Override",
            "Remove project-specific exclusions for this folder?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.clear_override_requested = True
            self.accept()

    def scope(self):
        return self.scopeCombo.currentData()

    def result_config(self):
        enabled_modules = [module_id for module_id, checkbox in self.module_checks.items() if checkbox.isChecked()]
        return {
            "preset_id": self.presetCombo.currentData(),
            "enabled_modules": enabled_modules,
            "custom_excluded_folders": self.customFoldersEditor.values(),
            "custom_excluded_files": self.customFilesEditor.values(),
            "custom_excluded_extensions": self.customExtensionsEditor.values(),
            "always_include_folders": self.includeFoldersEditor.values(),
            "always_include_files": self.includeFilesEditor.values(),
            "always_include_extensions": self.includeExtensionsEditor.values(),
        }


class UiLogic:
    def __init__(self, ui_setup, startup_folder="", app_title="Sleek Code Browser"):
        self.ui_setup = ui_setup
        self.app_title = app_title or "Sleek Code Browser"
        self.startup_folder = os.path.abspath(startup_folder) if startup_folder else ""
        self.settings = QSettings("SleekTools", "SleekCodeBrowser")
        self.bundle_entries = []
        self.bundle_text = ""
        self.bundle_positions = {}
        self.bundle_stats = self._empty_stats()
        self.skipped_files = []
        self.current_folder = ""
        self.current_effective_config = None
        self.auto_detected_preset_id = None
        self.current_theme = DEFAULT_THEME
        self.status_role = "normal"

        self._migrate_legacy_settings_ini()
        self.global_exclusion_config = self._load_global_exclusion_config()
        self.project_overrides = self._load_project_overrides()

        self.connect_signals()
        self._configure_platform_controls()
        self.restore_ui_state()

    def connect_signals(self):
        self.ui_setup.selectFolderButton.clicked.connect(self.selectFolder)
        self.ui_setup.refreshButton.clicked.connect(self.refreshFolder)
        self.ui_setup.expandCheckedButton.clicked.connect(self.expandCheckedFolders)
        self.ui_setup.buildBundleButton.clicked.connect(self.buildBundle)
        self.ui_setup.copyBundleButton.clicked.connect(self.copyBundle)
        self.ui_setup.exportBundleButton.clicked.connect(self.exportBundleTxt)
        self.ui_setup.manageExclusionsButton.clicked.connect(self.manageExclusions)
        self.ui_setup.windowsIntegrationButton.clicked.connect(self.manage_windows_integration)

        self.ui_setup.themeCombo.currentIndexChanged.connect(self._theme_selection_changed)
        self.ui_setup.bundleModeCombo.currentIndexChanged.connect(self._bundle_preferences_changed)
        self.ui_setup.includeEndMarkersCheck.toggled.connect(self._bundle_preferences_changed)

        self.ui_setup.nameFilterInput.textChanged.connect(self.applyTreeFilter)
        self.ui_setup.extensionFilterInput.textChanged.connect(self.applyTreeFilter)
        self.ui_setup.showCheckedOnlyCheck.toggled.connect(self.applyTreeFilter)
        self.ui_setup.fileTree.check_state_changed.connect(self.applyTreeFilter)
        self.ui_setup.fileTree.itemExpanded.connect(lambda _item: self.applyTreeFilter())

    def _configure_platform_controls(self):
        if os.name != "nt":
            self.ui_setup.windowsIntegrationButton.hide()

    def restore_ui_state(self):
        self._block_ui_pref_signals(True)
        saved_theme = normalize_theme(self.settings.value("ui/theme", DEFAULT_THEME, type=str))
        theme_index = self.ui_setup.themeCombo.findData(saved_theme)
        self.ui_setup.themeCombo.setCurrentIndex(theme_index if theme_index >= 0 else 0)
        self.set_theme(self.ui_setup.themeCombo.currentData(), persist=False)

        saved_mode = self.settings.value("bundle/mode", "ai_bundle", type=str)
        mode_index = self.ui_setup.bundleModeCombo.findData(saved_mode)
        self.ui_setup.bundleModeCombo.setCurrentIndex(mode_index if mode_index >= 0 else 0)
        self.ui_setup.includeEndMarkersCheck.setChecked(
            self.settings.value("bundle/include_end_markers", True, type=bool)
        )
        self._block_ui_pref_signals(False)

        splitter_sizes = self._load_json_value("ui/splitter_sizes", [])
        if splitter_sizes:
            self.ui_setup.splitter.setSizes([int(value) for value in splitter_sizes if int(value) > 0])

        window = self.ui_setup.mainWidget.window()
        saved_size = self.settings.value("ui/window_size")
        if saved_size is not None:
            window.resize(saved_size)
        saved_pos = self.settings.value("ui/window_pos")
        if saved_pos is not None:
            window.move(saved_pos)

        startup_folder = self._resolve_startup_folder()
        if startup_folder:
            self.open_folder(startup_folder, update_last=True)
        else:
            self.updateWindowTitle("")
            self.set_status("Select a folder to begin.")

    def save_ui_state(self):
        window = self.ui_setup.mainWidget.window()
        self.settings.setValue("ui/window_size", window.size())
        self.settings.setValue("ui/window_pos", window.pos())
        self._save_json_value("ui/splitter_sizes", self.ui_setup.splitter.sizes())
        if self.current_folder:
            self.settings.setValue("ui/last_folder", self.current_folder)
        self.settings.setValue("ui/theme", self.current_theme)
        self.settings.sync()

    def _block_ui_pref_signals(self, blocked):
        self.ui_setup.themeCombo.blockSignals(blocked)
        self.ui_setup.bundleModeCombo.blockSignals(blocked)
        self.ui_setup.includeEndMarkersCheck.blockSignals(blocked)

    def _resolve_startup_folder(self):
        if self.startup_folder and os.path.isdir(self.startup_folder):
            return self.startup_folder
        last_folder = self.settings.value("ui/last_folder", "", type=str)
        if last_folder and os.path.isdir(last_folder):
            return os.path.abspath(last_folder)
        return ""

    def _theme_selection_changed(self):
        self.set_theme(self.ui_setup.themeCombo.currentData(), persist=True)

    def set_theme(self, theme_name, persist=True):
        selected_theme = apply_theme(self.ui_setup.mainWidget.window(), theme_name)
        self.current_theme = selected_theme

        selected_index = self.ui_setup.themeCombo.findData(selected_theme)
        if selected_index >= 0 and self.ui_setup.themeCombo.currentIndex() != selected_index:
            was_blocked = self.ui_setup.themeCombo.blockSignals(True)
            self.ui_setup.themeCombo.setCurrentIndex(selected_index)
            self.ui_setup.themeCombo.blockSignals(was_blocked)

        if persist:
            self.settings.setValue("ui/theme", selected_theme)

        self._refresh_status_style()

    def _refresh_status_style(self):
        label = self.ui_setup.statusLabel
        label.setProperty("statusRole", self.status_role)
        label.style().unpolish(label)
        label.style().polish(label)
        label.update()

    def _bundle_preferences_changed(self):
        self.settings.setValue("bundle/mode", self.ui_setup.bundleModeCombo.currentData())
        self.settings.setValue("bundle/include_end_markers", self.ui_setup.includeEndMarkersCheck.isChecked())
        if self.bundle_entries:
            self._rebuild_bundle_from_entries()

    def _settings_ini_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini")

    def _migrate_legacy_settings_ini(self):
        if self.settings.value("migration/settings_ini_imported", False, type=bool):
            return

        legacy_ini = self._settings_ini_path()
        if not os.path.exists(legacy_ini):
            self.settings.setValue("migration/settings_ini_imported", True)
            return

        parser = configparser.ConfigParser()
        parser.read(legacy_ini)
        legacy_extensions = self._normalize_extension_list(
            parser.get("Extensions", "excluded", fallback="").split(",")
        )
        legacy_folders = self._normalize_name_list(parser.get("Exclusions", "folders", fallback="").split(","))
        legacy_files = self._normalize_name_list(parser.get("Exclusions", "files", fallback="").split(","))

        if legacy_extensions or legacy_folders or legacy_files:
            config = self._load_global_exclusion_config()
            config["custom_excluded_extensions"] = sorted(
                set(config["custom_excluded_extensions"]) | set(legacy_extensions)
            )
            config["custom_excluded_folders"] = sorted(set(config["custom_excluded_folders"]) | set(legacy_folders))
            config["custom_excluded_files"] = sorted(set(config["custom_excluded_files"]) | set(legacy_files))
            self._save_global_exclusion_config(config)

        self.settings.setValue("migration/settings_ini_imported", True)

    def _load_json_value(self, key, default_value):
        raw_value = self.settings.value(key, "")
        if raw_value in (None, ""):
            return copy.deepcopy(default_value)
        if isinstance(raw_value, (dict, list)):
            return raw_value
        try:
            return json.loads(raw_value)
        except (TypeError, ValueError, json.JSONDecodeError):
            return copy.deepcopy(default_value)

    def _save_json_value(self, key, value):
        self.settings.setValue(key, json.dumps(value))

    def _normalize_path(self, path):
        return os.path.normcase(os.path.abspath(path))

    def _normalize_name_list(self, values):
        normalized = []
        for value in values or []:
            text = str(value).strip().lower()
            if text:
                normalized.append(text)
        return sorted(set(normalized))

    def _normalize_extension_list(self, values):
        normalized = []
        for value in values or []:
            text = str(value).strip().lower()
            if not text:
                continue
            if not text.startswith("."):
                text = f".{text}"
            normalized.append(text)
        return sorted(set(normalized))

    def _default_exclusion_config(self):
        preset_id = "standard_code_project"
        return {
            "preset_id": preset_id,
            "enabled_modules": list(PRESET_DEFINITIONS[preset_id]["modules"]),
            "custom_excluded_folders": [],
            "custom_excluded_files": [],
            "custom_excluded_extensions": [],
            "always_include_folders": [],
            "always_include_files": [],
            "always_include_extensions": [],
        }

    def _normalize_exclusion_config(self, config):
        result = copy.deepcopy(config or {})
        preset_id = result.get("preset_id", "standard_code_project")
        if preset_id not in PRESET_DEFINITIONS:
            preset_id = "standard_code_project"
        result["preset_id"] = preset_id

        enabled_modules = result.get("enabled_modules")
        if not enabled_modules:
            enabled_modules = PRESET_DEFINITIONS[preset_id]["modules"]
        result["enabled_modules"] = [module for module in enabled_modules if module in EXCLUSION_MODULES]

        result["custom_excluded_folders"] = self._normalize_name_list(result.get("custom_excluded_folders", []))
        result["custom_excluded_files"] = self._normalize_name_list(result.get("custom_excluded_files", []))
        result["custom_excluded_extensions"] = self._normalize_extension_list(
            result.get("custom_excluded_extensions", [])
        )

        result["always_include_folders"] = self._normalize_name_list(result.get("always_include_folders", []))
        result["always_include_files"] = self._normalize_name_list(result.get("always_include_files", []))
        result["always_include_extensions"] = self._normalize_extension_list(result.get("always_include_extensions", []))
        return result

    def _load_global_exclusion_config(self):
        data = self._load_json_value("exclusions/global_config", self._default_exclusion_config())
        return self._normalize_exclusion_config(data)

    def _save_global_exclusion_config(self, config):
        normalized = self._normalize_exclusion_config(config)
        self._save_json_value("exclusions/global_config", normalized)

    def _load_project_overrides(self):
        raw_overrides = self._load_json_value("exclusions/project_overrides", {})
        normalized = {}
        if not isinstance(raw_overrides, dict):
            return normalized

        for path, config in raw_overrides.items():
            try:
                normalized[self._normalize_path(path)] = self._normalize_exclusion_config(config)
            except Exception:
                continue
        return normalized

    def _save_project_overrides(self):
        self._save_json_value("exclusions/project_overrides", self.project_overrides)

    def _has_project_override(self, folder_path):
        if not folder_path:
            return False
        return self._normalize_path(folder_path) in self.project_overrides

    def _detect_project_preset(self, folder_path):
        try:
            root_items = {name.lower() for name in os.listdir(folder_path)}
        except OSError:
            return "standard_code_project"

        if "composer.json" in root_items:
            return "php_web_server_project"

        if {"pyproject.toml", "requirements.txt", "setup.py", "setup.cfg"} & root_items:
            return "python_project"

        if "package.json" in root_items:
            frontend_markers = {
                "next.config.js",
                "next.config.mjs",
                "vite.config.js",
                "vite.config.ts",
                "nuxt.config.js",
                "nuxt.config.ts",
                "angular.json",
            }
            if frontend_markers & root_items:
                return "frontend_web_app"
            if "public" in root_items or "src" in root_items:
                return "frontend_web_app"
            return "node_tooling_full_stack"

        return "standard_code_project"

    def _get_effective_exclusion_config(self, folder_path):
        self.auto_detected_preset_id = None
        if not folder_path:
            return copy.deepcopy(self.global_exclusion_config)

        folder_key = self._normalize_path(folder_path)
        if folder_key in self.project_overrides:
            return copy.deepcopy(self.project_overrides[folder_key])

        config = copy.deepcopy(self.global_exclusion_config)
        detected_preset = self._detect_project_preset(folder_path)
        if detected_preset in PRESET_DEFINITIONS:
            self.auto_detected_preset_id = detected_preset
            config["preset_id"] = detected_preset
            config["enabled_modules"] = list(PRESET_DEFINITIONS[detected_preset]["modules"])
        return self._normalize_exclusion_config(config)

    def _build_exclusion_rules(self, config):
        folder_rules = set()
        file_rules = set()
        extension_rules = set()

        for module_id in config.get("enabled_modules", []):
            module = EXCLUSION_MODULES.get(module_id, {})
            folder_rules.update(self._normalize_name_list(module.get("folders", [])))
            file_rules.update(self._normalize_name_list(module.get("files", [])))
            extension_rules.update(self._normalize_extension_list(module.get("extensions", [])))

        folder_rules.update(config.get("custom_excluded_folders", []))
        file_rules.update(config.get("custom_excluded_files", []))
        extension_rules.update(config.get("custom_excluded_extensions", []))

        return {
            "folders": sorted(folder_rules),
            "files": sorted(file_rules),
            "extensions": sorted(extension_rules),
            "always_include_folders": config.get("always_include_folders", []),
            "always_include_files": config.get("always_include_files", []),
            "always_include_extensions": config.get("always_include_extensions", []),
        }

    def selectFolder(self):
        start_dir = self.current_folder or self.settings.value("ui/last_folder", "", type=str) or os.path.expanduser("~")
        folder_path = QFileDialog.getExistingDirectory(self.ui_setup.mainWidget, "Select Folder", start_dir)
        if folder_path:
            self.open_folder(folder_path)

    def _windows_launch_target(self):
        if getattr(sys, "frozen", False):
            executable = os.path.abspath(sys.executable)
            launch_dir = os.path.dirname(executable)
            return f'"{executable}"', launch_dir, executable

        python_executable = os.path.abspath(sys.executable)
        if python_executable.lower().endswith("python.exe"):
            pythonw_executable = python_executable[:-10] + "pythonw.exe"
            if os.path.exists(pythonw_executable):
                python_executable = pythonw_executable

        main_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
        launch_command = f'"{python_executable}" "{main_script}"'
        launch_dir = os.path.dirname(main_script)
        return launch_command, launch_dir, ""

    def _normalize_path_parts(self, path_value):
        return [part.strip() for part in path_value.split(";") if part.strip()]

    def _set_user_path_entry(self, folder_path, should_include):
        folder_norm = os.path.normcase(os.path.normpath(folder_path))
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            try:
                current_path, value_type = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path, value_type = "", winreg.REG_EXPAND_SZ

            parts = self._normalize_path_parts(str(current_path))
            normalized_parts = [os.path.normcase(os.path.normpath(part)) for part in parts]
            already_present = folder_norm in normalized_parts

            if should_include and not already_present:
                parts.append(folder_path)
            elif not should_include and already_present:
                parts = [part for part in parts if os.path.normcase(os.path.normpath(part)) != folder_norm]

            updated_path = ";".join(parts)
            winreg.SetValueEx(key, "Path", 0, value_type, updated_path)
        return already_present

    def _write_context_menu_key(self, key_path, menu_label, command_text, icon_value):
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, menu_label)
            if icon_value:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_value)
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, f"{key_path}\\command", 0, winreg.KEY_WRITE) as command_key:
            winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command_text)

    def _delete_registry_tree(self, key_path):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                while True:
                    try:
                        child_name = winreg.EnumKey(key, 0)
                    except OSError:
                        break
                    self._delete_registry_tree(f"{key_path}\\{child_name}")
        except FileNotFoundError:
            return
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
        except FileNotFoundError:
            pass

    def _broadcast_environment_change(self):
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        try:
            ctypes.windll.user32.SendMessageTimeoutW(  # pylint: disable=no-member
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                "Environment",
                SMTO_ABORTIFHUNG,
                5000,
                None,
            )
        except Exception:
            pass

    def _install_windows_integration(self):
        launch_command, launch_dir, icon_value = self._windows_launch_target()
        command_on_folder = f'{launch_command} "%1"'
        command_in_folder = f'{launch_command} "%V"'

        self._write_context_menu_key(
            r"Software\Classes\Directory\shell\SleekHere",
            "Sleek Here",
            command_on_folder,
            icon_value,
        )
        self._write_context_menu_key(
            r"Software\Classes\Directory\Background\shell\SleekHere",
            "Sleek Here",
            command_in_folder,
            icon_value,
        )

        already_present = self._set_user_path_entry(launch_dir, should_include=True)
        self._broadcast_environment_change()
        return launch_dir, already_present

    def _remove_windows_integration(self):
        _, launch_dir, _ = self._windows_launch_target()
        self._delete_registry_tree(r"Software\Classes\Directory\shell\SleekHere")
        self._delete_registry_tree(r"Software\Classes\Directory\Background\shell\SleekHere")
        had_path_entry = self._set_user_path_entry(launch_dir, should_include=False)
        self._broadcast_environment_change()
        return launch_dir, had_path_entry

    def manage_windows_integration(self):
        if os.name != "nt":
            self.set_status("Windows integration is only available on Windows.", warning=True)
            return

        message_box = QMessageBox(self.ui_setup.mainWidget)
        message_box.setIcon(QMessageBox.Question)
        message_box.setWindowTitle("Windows Integration")
        message_box.setText("Choose a Windows integration action.")
        install_button = message_box.addButton("Install / Update", QMessageBox.AcceptRole)
        remove_button = message_box.addButton("Remove", QMessageBox.DestructiveRole)
        message_box.addButton(QMessageBox.Cancel)
        message_box.exec_()

        clicked_button = message_box.clickedButton()
        if clicked_button == install_button:
            try:
                launch_dir, already_present = self._install_windows_integration()
            except Exception as error:
                self.set_status(f"Windows integration failed: {error}", warning=True)
                QMessageBox.critical(
                    self.ui_setup.mainWidget,
                    "Windows Integration",
                    f"Install/update failed.\n\n{error}",
                )
                return

            path_note = "already in PATH" if already_present else "added to PATH"
            self.set_status(f"Windows integration installed. {launch_dir} {path_note}.")
            QMessageBox.information(
                self.ui_setup.mainWidget,
                "Windows Integration",
                "Installed:\n- Explorer context menu: Sleek Here\n- User PATH updated\n\n"
                "You may need to restart open Explorer/terminal windows.",
            )
        elif clicked_button == remove_button:
            try:
                launch_dir, had_path_entry = self._remove_windows_integration()
            except Exception as error:
                self.set_status(f"Removing integration failed: {error}", warning=True)
                QMessageBox.critical(
                    self.ui_setup.mainWidget,
                    "Windows Integration",
                    f"Removal failed.\n\n{error}",
                )
                return

            path_note = "removed from PATH" if had_path_entry else "not present in PATH"
            self.set_status(f"Windows integration removed. {launch_dir} {path_note}.")
            QMessageBox.information(
                self.ui_setup.mainWidget,
                "Windows Integration",
                "Removed Explorer context menu and updated user PATH.",
            )

    def open_folder(self, folder_path, update_last=True):
        absolute_path = os.path.abspath(folder_path)
        if not os.path.isdir(absolute_path):
            self.set_status("Selected path is not a folder.", warning=True)
            return

        self.current_folder = absolute_path
        if update_last:
            self.settings.setValue("ui/last_folder", absolute_path)

        self.clear_bundle_output()
        self.populateFileTree(absolute_path)
        self.updateWindowTitle(absolute_path)

        preset_id = self.current_effective_config["preset_id"]
        preset_label = PRESET_DEFINITIONS[preset_id]["label"]
        scope_label = "project override" if self._has_project_override(absolute_path) else "global/auto preset"
        self.set_status(f"Loaded {os.path.basename(absolute_path) or absolute_path} with {preset_label} ({scope_label}).")

    def refreshFolder(self):
        if not self.current_folder or not os.path.isdir(self.current_folder):
            return

        state_overrides = self.ui_setup.fileTree.capture_check_states()
        self.populateFileTree(self.current_folder, state_overrides=state_overrides)
        self.set_status("Refresh complete. Previous check states restored where possible.")

    def populateFileTree(self, folder_path, state_overrides=None):
        self.current_effective_config = self._get_effective_exclusion_config(folder_path)
        exclusion_rules = self._build_exclusion_rules(self.current_effective_config)
        self.ui_setup.fileTree.populate(folder_path, exclusion_rules=exclusion_rules, state_overrides=state_overrides)
        self.applyTreeFilter()

        if self.ui_setup.fileTree.folder_errors:
            error_count = len(self.ui_setup.fileTree.folder_errors)
            self.set_status(f"{error_count} folder(s) could not be read during load.", warning=True)

    def updateWindowTitle(self, folder_path):
        if folder_path:
            folder_name = os.path.basename(folder_path) or folder_path
            self.ui_setup.mainWidget.window().setWindowTitle(f"{self.app_title} - {folder_name}")
        else:
            self.ui_setup.mainWidget.window().setWindowTitle(self.app_title)

    def applyTreeFilter(self):
        self.ui_setup.fileTree.set_filter(
            self.ui_setup.nameFilterInput.text(),
            self.ui_setup.extensionFilterInput.text(),
            self.ui_setup.showCheckedOnlyCheck.isChecked(),
        )

    def _empty_stats(self):
        return {"files": 0, "chars": 0, "bytes": 0, "lines": 0, "tokens": 0}

    def clearTabs(self):
        while self.ui_setup.tabLayout.count():
            item = self.ui_setup.tabLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def clear_bundle_output(self):
        self.bundle_entries = []
        self.bundle_text = ""
        self.bundle_positions = {}
        self.bundle_stats = self._empty_stats()
        self.skipped_files = []

        self.clearTabs()
        self.ui_setup.textArea.clear()
        self.ui_setup.statsLabel.setText("0 files | 0 chars | 0 bytes | 0 lines | ~0 tokens")
        self.ui_setup.sizeIndicatorLabel.setText("Ready")

    def _is_likely_binary(self, content_bytes):
        if not content_bytes:
            return False

        sample = content_bytes[:8192]
        if b"\x00" in sample:
            return True

        text_bytes = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
        non_text = sum(byte not in text_bytes for byte in sample)
        return (non_text / len(sample)) > 0.30

    def _read_text_file(self, file_path):
        try:
            with open(file_path, "rb") as file_handle:
                content_bytes = file_handle.read()
        except OSError as error:
            return None, f"unreadable ({error})"

        if self._is_likely_binary(content_bytes):
            return None, "binary"

        for encoding in ("utf-8", "utf-8-sig", "cp1252"):
            try:
                return content_bytes.decode(encoding), None
            except UnicodeDecodeError:
                continue

        return content_bytes.decode("utf-8", errors="replace"), None

    def _relative_path(self, file_path):
        try:
            relative_path = os.path.relpath(file_path, self.current_folder)
            if relative_path.startswith(".."):
                raise ValueError("outside root")
        except Exception:
            relative_path = os.path.basename(file_path)
        return relative_path.replace("\\", "/")

    def _comment_style_for_file(self, file_path):
        extension = os.path.splitext(file_path)[1].lower()
        if extension in SLASH_STYLE_EXTENSIONS:
            return "slash"
        if extension in CSS_STYLE_EXTENSIONS:
            return "css"
        if extension in HTML_STYLE_EXTENSIONS:
            return "html"
        if extension in SQL_STYLE_EXTENSIONS:
            return "sql"
        if extension in REM_STYLE_EXTENSIONS:
            return "rem"
        if extension in HASH_STYLE_EXTENSIONS:
            return "hash"
        return "hash"

    def _format_marker(self, style, message):
        if style == "slash":
            return f"// {message}"
        if style == "css":
            return f"/* {message} */"
        if style == "html":
            return f"<!-- {message} -->"
        if style == "sql":
            return f"-- {message}"
        if style == "rem":
            return f"REM {message}"
        return f"# {message}"

    def _build_file_section(self, file_path, relative_path, content):
        mode = self.ui_setup.bundleModeCombo.currentData()
        include_end_markers = self.ui_setup.includeEndMarkersCheck.isChecked()

        if mode == "language_safe":
            marker_style = self._comment_style_for_file(file_path)
            start_marker = self._format_marker(marker_style, f"===== BEGIN FILE: {relative_path} =====")
            end_marker = self._format_marker(marker_style, f"===== END FILE: {relative_path} =====")
        else:
            start_marker = f"# ===== BEGIN FILE: {relative_path} ====="
            end_marker = f"# ===== END FILE: {relative_path} ====="

        section_parts = [start_marker, "\n", content]
        if content and not content.endswith("\n"):
            section_parts.append("\n")

        if include_end_markers:
            section_parts.extend([end_marker, "\n"])

        section_parts.append("\n")
        section_text = "".join(section_parts)
        return section_text, start_marker

    def _estimate_tokens(self, character_count):
        if character_count <= 0:
            return 0
        return int(math.ceil(character_count / 4.0))

    def _text_stats(self, text):
        character_count = len(text)
        line_count = text.count("\n")
        if text and not text.endswith("\n"):
            line_count += 1
        return {
            "files": 1,
            "chars": character_count,
            "bytes": len(text.encode("utf-8")),
            "lines": line_count,
            "tokens": self._estimate_tokens(character_count),
        }

    def _aggregate_stats(self, stats_items):
        aggregate = self._empty_stats()
        for item in stats_items:
            aggregate["files"] += item.get("files", 0)
            aggregate["chars"] += item.get("chars", 0)
            aggregate["bytes"] += item.get("bytes", 0)
            aggregate["lines"] += item.get("lines", 0)
            aggregate["tokens"] += item.get("tokens", 0)
        return aggregate

    def _finalize_bundle(self, entries):
        parts = []
        positions = {}
        cursor = 0
        for entry in entries:
            positions[entry["relative_path"]] = cursor
            parts.append(entry["section"])
            cursor += len(entry["section"])
        bundle_text = "".join(parts)
        bundle_stats = self._aggregate_stats([entry["stats"] for entry in entries])
        return bundle_text, positions, bundle_stats

    def _rebuild_bundle_from_entries(self):
        if not self.bundle_entries:
            return
        for entry in self.bundle_entries:
            section_text, start_marker = self._build_file_section(
                entry["file_path"], entry["relative_path"], entry["content"]
            )
            entry["start_marker"] = start_marker
            entry["section"] = section_text
            entry["stats"] = self._text_stats(section_text)
        self._render_bundle_output()

    def buildBundle(self):
        if not self.current_folder:
            self.set_status("Select a folder before building a bundle.", warning=True)
            return

        checked_files = self.ui_setup.fileTree.get_checked_file_paths()
        if not checked_files:
            self.clear_bundle_output()
            self.set_status("No checked files to include in the bundle.", warning=True)
            return

        self.bundle_entries = []
        self.skipped_files = []

        for file_path in checked_files:
            content, skip_reason = self._read_text_file(file_path)
            if skip_reason:
                self.skipped_files.append((file_path, skip_reason))
                continue

            relative_path = self._relative_path(file_path)
            self.bundle_entries.append(
                {
                    "file_path": file_path,
                    "content": content,
                    "relative_path": relative_path,
                    "start_marker": "",
                    "section": "",
                    "stats": self._empty_stats(),
                }
            )

        if not self.bundle_entries:
            self.clear_bundle_output()
            self.set_status("No readable text files were selected.", warning=True)
            return

        self._rebuild_bundle_from_entries()

        loaded_files = len(self.bundle_entries)
        skipped_count = len(self.skipped_files)
        message = f"Loaded {loaded_files} file(s) into bundle."
        if skipped_count:
            message += f" Skipped {skipped_count} binary/unreadable file(s)."
        if self.ui_setup.fileTree.folder_errors:
            message += f" {len(self.ui_setup.fileTree.folder_errors)} folder(s) could not be read."
        self.set_status(message, warning=bool(skipped_count or self.ui_setup.fileTree.folder_errors))

    def _render_bundle_output(self):
        self.bundle_text, self.bundle_positions, self.bundle_stats = self._finalize_bundle(self.bundle_entries)
        self.ui_setup.textArea.setPlainText(self.bundle_text)

        self.clearTabs()
        for entry in self.bundle_entries:
            label = os.path.basename(entry["relative_path"]) or entry["relative_path"]
            jump_button = QPushButton(label)
            jump_button.setToolTip(entry["relative_path"])
            position = self.bundle_positions.get(entry["relative_path"], 0)
            jump_button.clicked.connect(
                lambda _checked=False, cursor_position=position: self.scrollToPosition(cursor_position)
            )
            self.ui_setup.tabLayout.addWidget(jump_button)

        self._update_stats_and_warnings()

    def _update_stats_and_warnings(self):
        stats = self.bundle_stats
        stats_text = (
            f"{stats['files']} files | {stats['chars']:,} chars | "
            f"{stats['bytes']:,} bytes | {stats['lines']:,} lines | "
            f"~{stats['tokens']:,} tokens"
        )
        self.ui_setup.statsLabel.setText(stats_text)

        if stats["tokens"] >= HARD_TOKEN_WARNING:
            self.ui_setup.sizeIndicatorLabel.setText("Hard warning: likely too large for one paste.")
        elif stats["tokens"] >= SOFT_TOKEN_WARNING:
            self.ui_setup.sizeIndicatorLabel.setText("Soft warning: high token count.")
        else:
            self.ui_setup.sizeIndicatorLabel.setText("Normal")

    def scrollToPosition(self, position):
        cursor = self.ui_setup.textArea.textCursor()
        cursor.setPosition(max(0, position))
        self.ui_setup.textArea.setTextCursor(cursor)
        self.ui_setup.textArea.centerCursor()

    def copyBundle(self):
        text = self.bundle_text or self.ui_setup.textArea.toPlainText()
        if not text:
            self.set_status("No bundle content to copy.", warning=True)
            return

        app = QApplication.instance()
        clipboard = app.clipboard() if app is not None else None
        if clipboard is None:
            self.set_status("Clipboard is unavailable right now.", warning=True)
            return

        try:
            clipboard.setText(text)
        except Exception as error:
            self.set_status(f"Copy failed: {error}", warning=True)
            return

        self.set_status(f"Copied bundle to clipboard ({len(text):,} chars).")

    def _default_export_filename(self):
        folder_name = os.path.basename(self.current_folder or "").strip().lower()
        safe_name = re.sub(r"[^a-z0-9._-]+", "-", folder_name).strip("-")
        if not safe_name:
            safe_name = "bundle"
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
        return f"{safe_name}-bundle-{timestamp}.txt"

    def exportBundleTxt(self):
        text = self.bundle_text or self.ui_setup.textArea.toPlainText()
        if not text:
            self.set_status("No bundle content to export.", warning=True)
            QMessageBox.warning(
                self.ui_setup.mainWidget,
                "Export Bundle to TXT",
                "Build a bundle first, then export it.",
            )
            return

        default_name = self._default_export_filename()
        last_dir = self.settings.value("export/last_dir", "", type=str)
        start_dir = last_dir or self.current_folder or os.path.expanduser("~")
        initial_path = os.path.join(start_dir, default_name)

        save_path, _ = QFileDialog.getSaveFileName(
            self.ui_setup.mainWidget,
            "Export Bundle to TXT",
            initial_path,
            "Text Files (*.txt);;All Files (*)",
        )
        if not save_path:
            self.set_status("Export cancelled.")
            return

        if not save_path.lower().endswith(".txt"):
            save_path = f"{save_path}.txt"

        try:
            with open(save_path, "w", encoding="utf-8") as handle:
                handle.write(text)
        except OSError as error:
            self.set_status(f"Export failed: {error}", warning=True)
            QMessageBox.critical(
                self.ui_setup.mainWidget,
                "Export Bundle to TXT",
                f"Could not write the file.\n\n{error}",
            )
            return

        self.settings.setValue("export/last_dir", os.path.dirname(save_path))
        self.set_status(f"Exported bundle TXT: {save_path}")

    def expandCheckedFolders(self):
        self.ui_setup.fileTree.expand_checked_folders()

    def manageExclusions(self):
        initial_config = copy.deepcopy(self.current_effective_config or self.global_exclusion_config)
        has_override = self._has_project_override(self.current_folder)
        dialog = ExclusionsDialog(
            initial_config=initial_config,
            current_folder=self.current_folder,
            has_project_override=has_override,
            auto_detected_preset=self.auto_detected_preset_id,
            parent=self.ui_setup.mainWidget,
        )

        if dialog.exec_() != QDialog.Accepted:
            return

        folder_key = self._normalize_path(self.current_folder) if self.current_folder else ""
        if dialog.clear_override_requested:
            if folder_key and folder_key in self.project_overrides:
                del self.project_overrides[folder_key]
                self._save_project_overrides()
                self.set_status("Project override cleared.")
                if self.current_folder:
                    self.clear_bundle_output()
                    self.populateFileTree(self.current_folder)
            return

        new_config = self._normalize_exclusion_config(dialog.result_config())
        if dialog.scope() == "project" and self.current_folder:
            self.project_overrides[folder_key] = new_config
            self._save_project_overrides()
            self.set_status("Saved project-specific exclusions.")
        else:
            self.global_exclusion_config = new_config
            self._save_global_exclusion_config(new_config)
            if self.current_folder and self._has_project_override(self.current_folder):
                self.set_status("Saved global exclusions. Current folder still uses its project override.")
            else:
                self.set_status("Saved global exclusions.")

        if self.current_folder:
            self.clear_bundle_output()
            self.populateFileTree(self.current_folder)

    def set_status(self, message, warning=False):
        self.ui_setup.statusLabel.setText(message)
        self.status_role = "warning" if warning else "normal"
        self._refresh_status_style()
