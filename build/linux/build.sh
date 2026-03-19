#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"

version_file="$repo_root/VERSION"
if [[ ! -f "$version_file" ]]; then
  echo "VERSION file is missing at $version_file" >&2
  exit 1
fi

version="$(tr -d '[:space:]' < "$version_file")"
if [[ -z "$version" ]]; then
  echo "VERSION file is empty." >&2
  exit 1
fi

dist_dir="$repo_root/dist"
stage_root="$repo_root/packaging/debian/sleek-code-browser"
artifact_path="$dist_dir/sleek-code-browser_${version}_amd64.deb"

echo "Building Linux executable with PyInstaller..."
pushd "$repo_root" >/dev/null
python -m PyInstaller main.py --name sleek --onefile --noconfirm --clean --add-data "icon.ico:." --add-data "VERSION:."
popd >/dev/null

rm -rf "$stage_root"
mkdir -p \
  "$stage_root/DEBIAN" \
  "$stage_root/usr/bin" \
  "$stage_root/opt/sleek-code-browser" \
  "$stage_root/usr/share/applications" \
  "$stage_root/usr/share/icons/hicolor/256x256/apps"

install -m 755 "$dist_dir/sleek" "$stage_root/opt/sleek-code-browser/sleek"
install -m 755 "$repo_root/packaging/debian/sleek-launcher.sh" "$stage_root/usr/bin/sleek"
install -m 644 "$repo_root/packaging/debian/sleek-code-browser.desktop" \
  "$stage_root/usr/share/applications/sleek-code-browser.desktop"
install -m 644 "$repo_root/icon.ico" "$stage_root/opt/sleek-code-browser/icon.ico"

sed "s/@VERSION@/$version/g" "$repo_root/packaging/debian/control.in" > "$stage_root/DEBIAN/control"
chmod 755 "$stage_root/DEBIAN"

if command -v convert >/dev/null 2>&1; then
  convert "$repo_root/icon.ico[0]" -background none -resize 256x256 \
    "$stage_root/usr/share/icons/hicolor/256x256/apps/sleek-code-browser.png"
else
  python - <<PY
from PyQt5.QtGui import QIcon
icon = QIcon(r"$repo_root/icon.ico")
pixmap = icon.pixmap(256, 256)
if pixmap.isNull():
    raise SystemExit("Failed to render icon.ico into a PNG icon.")
if not pixmap.save(r"$stage_root/usr/share/icons/hicolor/256x256/apps/sleek-code-browser.png", "PNG"):
    raise SystemExit("Failed to save sleek-code-browser.png.")
PY
fi

dpkg-deb --build --root-owner-group "$stage_root" "$artifact_path"
echo "Ubuntu package ready: $artifact_path"
