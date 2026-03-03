import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class DirectoryView(QTreeWidget):
    check_state_changed = pyqtSignal()
    PLACEHOLDER_TEXT = "Loading..."

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.folder_path = ""
        self.folder_errors = []
        self._path_type_cache = {}
        self._rules = self._normalize_rules(None)
        self._state_overrides = {}
        self._suppress_item_changed = False
        self._name_filter = ""
        self._extension_filter = ""
        self._show_checked_only = False
        self.itemExpanded.connect(self.on_item_expanded)
        self.itemChanged.connect(self.on_item_changed)

    def populate(self, folder_path, exclusion_rules=None, state_overrides=None):
        self.clear()
        self.folder_errors = []
        self._path_type_cache = {}
        self.folder_path = os.path.abspath(folder_path) if folder_path else ""
        self._rules = self._normalize_rules(exclusion_rules)
        self._state_overrides = self._normalize_state_overrides(state_overrides)

        if not self.folder_path:
            return
        self._path_type_cache[self._normalize_path(self.folder_path)] = True

        self._suppress_item_changed = True
        self.add_directory_items(self.invisibleRootItem(), self.folder_path, lazy_load=True)
        self._recompute_parent_states(self.invisibleRootItem())
        self._suppress_item_changed = False
        self.apply_active_filter()

    def _normalize_state_overrides(self, state_overrides):
        normalized = {}
        if not state_overrides:
            return normalized

        for path, state in state_overrides.items():
            try:
                normalized[self._normalize_path(path)] = int(state)
            except (TypeError, ValueError):
                continue
        return normalized

    def _normalize_rules(self, rules):
        base = rules or {}
        return {
            "folders": self._normalize_names(base.get("folders")),
            "files": self._normalize_names(base.get("files")),
            "extensions": self._normalize_extensions(base.get("extensions")),
            "always_include_folders": self._normalize_names(base.get("always_include_folders")),
            "always_include_files": self._normalize_names(base.get("always_include_files")),
            "always_include_extensions": self._normalize_extensions(base.get("always_include_extensions")),
        }

    def _normalize_names(self, values):
        normalized = set()
        for value in values or []:
            text = self._normalize_rule_path(value)
            if text:
                normalized.add(text)
        return normalized

    def _normalize_rule_path(self, value):
        text = str(value).strip().lower().replace("\\", "/")
        if not text:
            return ""

        parts = [part for part in text.split("/") if part and part != "."]
        return "/".join(parts)

    def _normalize_extensions(self, values):
        normalized = set()
        for value in values or []:
            text = str(value).strip().lower()
            if not text:
                continue
            if not text.startswith("."):
                text = f".{text}"
            normalized.add(text)
        return normalized

    def _normalize_path(self, path):
        return os.path.normcase(os.path.abspath(path))

    def _relative_rule_key(self, file_path):
        if not file_path:
            return ""

        base_folder = self.folder_path or ""
        try:
            if base_folder:
                relative = os.path.relpath(file_path, base_folder)
            else:
                relative = os.path.basename(file_path)
        except ValueError:
            relative = os.path.basename(file_path)

        return self._normalize_rule_path(relative)

    def _record_folder_error(self, path, error):
        entry = (path, str(error))
        if entry not in self.folder_errors:
            self.folder_errors.append(entry)

    def _safe_is_directory(self, path):
        if not path:
            return False
        normalized_path = self._normalize_path(path)
        cached_value = self._path_type_cache.get(normalized_path)
        if cached_value is not None:
            return cached_value
        try:
            is_directory = os.path.isdir(path)
            self._path_type_cache[normalized_path] = is_directory
            return is_directory
        except OSError as error:
            self._record_folder_error(path, error)
            self._path_type_cache[normalized_path] = False
            return False

    def _is_directory_path(self, path):
        return self._safe_is_directory(path)

    def _entry_is_directory(self, entry):
        try:
            return entry.is_dir(follow_symlinks=False)
        except OSError as error:
            self._record_folder_error(entry.path, error)
            return False

    def _get_override_state(self, path):
        return self._state_overrides.get(self._normalize_path(path))

    def add_directory_items(self, parent_item, folder_path, lazy_load=False):
        self._remove_placeholder_if_present(parent_item)
        parent_state = self._item_state(parent_item)

        try:
            with os.scandir(folder_path) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name.lower())
        except Exception as error:
            self._record_folder_error(folder_path, error)
            return

        existing_items = self._existing_child_paths(parent_item)
        for entry in entries:
            file_name = entry.name
            file_path = entry.path
            normalized_path = self._normalize_path(file_path)
            if normalized_path in existing_items:
                continue

            is_directory = self._entry_is_directory(entry)
            self._path_type_cache[normalized_path] = is_directory
            item = QTreeWidgetItem(parent_item)
            item.setData(0, Qt.UserRole, file_path)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            item.setText(0, f"📁 {file_name}" if is_directory else f"📄 {file_name}")
            item.setCheckState(0, self._initial_check_state(file_path, file_name, is_directory, parent_state))

            if is_directory:
                if lazy_load:
                    item.addChild(self._create_placeholder_item())
                else:
                    self.add_directory_items(item, file_path, lazy_load=False)

    def _existing_child_paths(self, parent_item):
        existing = set()
        for index in range(parent_item.childCount()):
            child = parent_item.child(index)
            path = child.data(0, Qt.UserRole)
            if path:
                existing.add(self._normalize_path(path))
        return existing

    def _initial_check_state(self, file_path, file_name, is_directory, parent_state):
        override_state = self._get_override_state(file_path)
        if override_state in (Qt.Checked, Qt.Unchecked, Qt.PartiallyChecked):
            return override_state

        if self._is_excluded(file_path, file_name, is_directory):
            return Qt.Unchecked

        if parent_state in (Qt.Checked, Qt.Unchecked):
            return parent_state

        return Qt.Checked

    def _is_excluded(self, file_path, file_name, is_directory):
        lower_name = self._normalize_rule_path(file_name)
        relative_key = self._relative_rule_key(file_path)
        extension = os.path.splitext(lower_name)[1]

        if is_directory:
            if lower_name in self._rules["always_include_folders"] or relative_key in self._rules["always_include_folders"]:
                return False
            return lower_name in self._rules["folders"] or relative_key in self._rules["folders"]

        if (
            lower_name in self._rules["always_include_files"]
            or relative_key in self._rules["always_include_files"]
            or extension in self._rules["always_include_extensions"]
        ):
            return False

        return (
            lower_name in self._rules["files"]
            or relative_key in self._rules["files"]
            or extension in self._rules["extensions"]
        )

    def _item_state(self, item):
        if item is None or item is self.invisibleRootItem():
            return None
        return item.checkState(0)

    def _create_placeholder_item(self):
        placeholder = QTreeWidgetItem([self.PLACEHOLDER_TEXT])
        placeholder.setFlags(Qt.ItemIsEnabled)
        placeholder.setData(0, Qt.UserRole, None)
        return placeholder

    def _has_placeholder(self, item):
        for index in range(item.childCount()):
            child = item.child(index)
            if child.data(0, Qt.UserRole) is None and child.text(0) == self.PLACEHOLDER_TEXT:
                return True
        return False

    def _remove_placeholder_if_present(self, item):
        if item is None:
            return

        indexes_to_remove = []
        for index in range(item.childCount()):
            child = item.child(index)
            if child.data(0, Qt.UserRole) is None and child.text(0) == self.PLACEHOLDER_TEXT:
                indexes_to_remove.append(index)

        for index in reversed(indexes_to_remove):
            item.takeChild(index)

    def on_item_expanded(self, item):
        if not self._has_placeholder(item):
            return

        folder_path = item.data(0, Qt.UserRole)
        if not self._is_directory_path(folder_path):
            return

        previous_state = self._suppress_item_changed
        self._suppress_item_changed = True
        self.add_directory_items(item, folder_path, lazy_load=True)
        self._suppress_item_changed = previous_state
        self.apply_active_filter()

    def on_item_changed(self, item, _column):
        if self._suppress_item_changed:
            return

        file_path = item.data(0, Qt.UserRole)
        if not file_path:
            return

        state = item.checkState(0)
        self._suppress_item_changed = True
        if self._is_directory_path(file_path) and state in (Qt.Checked, Qt.Unchecked):
            self.ensure_children_loaded(item, recursive=True)
            self._apply_state_to_descendants(item, state)
        self._update_parent_states(item.parent())
        self._suppress_item_changed = False

        self.apply_active_filter()
        self.check_state_changed.emit()

    def _apply_state_to_descendants(self, parent_item, state):
        for index in range(parent_item.childCount()):
            child = parent_item.child(index)
            child_path = child.data(0, Qt.UserRole)
            if not child_path:
                continue

            child.setCheckState(0, state)
            if self._is_directory_path(child_path):
                self._apply_state_to_descendants(child, state)

    def _update_parent_states(self, item):
        while item and item is not self.invisibleRootItem():
            child_states = []
            for index in range(item.childCount()):
                child = item.child(index)
                if child.data(0, Qt.UserRole):
                    child_states.append(child.checkState(0))

            if child_states:
                if all(state == Qt.Checked for state in child_states):
                    item.setCheckState(0, Qt.Checked)
                elif all(state == Qt.Unchecked for state in child_states):
                    item.setCheckState(0, Qt.Unchecked)
                else:
                    item.setCheckState(0, Qt.PartiallyChecked)
            item = item.parent()

    def _recompute_parent_states(self, parent_item):
        for index in range(parent_item.childCount()):
            child = parent_item.child(index)
            child_path = child.data(0, Qt.UserRole)
            if self._is_directory_path(child_path) and not self._has_placeholder(child):
                self._recompute_parent_states(child)
        self._update_parent_states(parent_item)

    def ensure_children_loaded(self, item, recursive=False):
        folder_path = item.data(0, Qt.UserRole)
        if not self._is_directory_path(folder_path):
            return

        if self._has_placeholder(item):
            self.add_directory_items(item, folder_path, lazy_load=not recursive)

        if recursive:
            for index in range(item.childCount()):
                child = item.child(index)
                child_path = child.data(0, Qt.UserRole)
                if self._is_directory_path(child_path):
                    self.ensure_children_loaded(child, recursive=True)

    def get_checked_file_paths(self):
        checked_files = []
        seen = set()
        self._collect_checked_files(self.invisibleRootItem(), checked_files, seen)
        return checked_files

    def _collect_checked_files(self, parent_item, checked_files, seen):
        for index in range(parent_item.childCount()):
            child = parent_item.child(index)
            file_path = child.data(0, Qt.UserRole)
            if not file_path:
                continue

            if self._is_directory_path(file_path):
                if child.checkState(0) != Qt.Unchecked:
                    self.ensure_children_loaded(child, recursive=True)
                    self._collect_checked_files(child, checked_files, seen)
            else:
                if child.checkState(0) == Qt.Checked:
                    normalized_path = self._normalize_path(file_path)
                    if normalized_path not in seen:
                        seen.add(normalized_path)
                        checked_files.append(file_path)

    def capture_check_states(self):
        states = {}
        self._capture_item_states(self.invisibleRootItem(), states)
        return states

    def _capture_item_states(self, parent_item, states):
        for index in range(parent_item.childCount()):
            child = parent_item.child(index)
            file_path = child.data(0, Qt.UserRole)
            if not file_path:
                continue

            states[file_path] = int(child.checkState(0))
            if self._is_directory_path(file_path) and not self._has_placeholder(child):
                self._capture_item_states(child, states)

    def set_filter(self, name_filter="", extension_filter="", show_checked_only=False):
        self._name_filter = name_filter.strip().lower()
        self._extension_filter = extension_filter.strip().lower()
        if self._extension_filter and not self._extension_filter.startswith("."):
            self._extension_filter = f".{self._extension_filter}"
        self._show_checked_only = bool(show_checked_only)
        self.apply_active_filter()

    def apply_active_filter(self):
        root = self.invisibleRootItem()
        for index in range(root.childCount()):
            self._apply_filter_to_item(root.child(index))

    def _apply_filter_to_item(self, item):
        file_path = item.data(0, Qt.UserRole)
        if not file_path:
            item.setHidden(True)
            return False

        basename = os.path.basename(file_path).lower()
        is_directory = self._is_directory_path(file_path)
        name_match = not self._name_filter or self._name_filter in basename
        checked_match = not self._show_checked_only or item.checkState(0) != Qt.Unchecked

        if is_directory:
            child_visible = False
            for index in range(item.childCount()):
                child = item.child(index)
                child_path = child.data(0, Qt.UserRole)
                if child_path and self._apply_filter_to_item(child):
                    child_visible = True

            potential_descendant_match = self._has_placeholder(item)
            if self._show_checked_only and item.checkState(0) == Qt.Unchecked:
                potential_descendant_match = False

            visible = (name_match and checked_match) or child_visible or potential_descendant_match
        else:
            extension = os.path.splitext(basename)[1]
            extension_match = not self._extension_filter or extension == self._extension_filter
            visible = name_match and extension_match and checked_match

        item.setHidden(not visible)
        return visible

    def expand_checked_folders(self):
        root = self.invisibleRootItem()
        for index in range(root.childCount()):
            self._expand_checked_recursive(root.child(index))

    def _expand_checked_recursive(self, item):
        file_path = item.data(0, Qt.UserRole)
        if not self._is_directory_path(file_path):
            return item.checkState(0) == Qt.Checked

        if self._has_placeholder(item):
            self.ensure_children_loaded(item, recursive=False)

        has_checked_descendant = False
        for index in range(item.childCount()):
            child = item.child(index)
            if self._expand_checked_recursive(child):
                has_checked_descendant = True

        if item.checkState(0) == Qt.Checked or has_checked_descendant:
            item.setExpanded(True)
            return True
        return False
