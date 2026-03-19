# Sleek Code Browser

Sleek Code Browser is a PyQt desktop app for creating prompt-ready source bundles from checked files in a project tree.

## Highlights

- Bundle modes:
  - `AI Bundle Mode`
  - `Language-Safe Mode`
- Bundle actions:
  - `Build Bundle`
  - `Copy Bundle`
  - `Export TXT`
- Startup folder precedence:
  1. explicit CLI path argument
  2. current working directory
  3. saved last folder
- Theme system:
  - `Light` (default)
  - `Dark`
  - persisted under `ui/theme`
- Optional Windows integration tools (installer-first, in-app repair on Windows).

## CLI Usage

```bash
sleek /path/to/project
sleek /path/to/file.py
```

If no argument is passed, Sleek opens the shell working directory when valid.

## Run From Source

```bash
python main.py
python main.py /path/to/project
```

## Version Source

Release/versioning is controlled by the top-level `VERSION` file.

## Build Artifacts

### Windows

- Build executable + installer:

```powershell
./build/windows/build.ps1
```

- Output:
  - `dist/SleekCodeBrowser-Setup-<version>.exe`

### Ubuntu

- Build onefile binary + `.deb`:

```bash
./build/linux/build.sh
```

- Output:
  - `dist/sleek-code-browser_<version>_amd64.deb`

## Installer Integration

### Windows installer

Installer tasks (both checked by default):

- `Add Sleek to PATH`
- `Add Sleek to Explorer context menu`

Context menu installs `Sleek Here` for:

- folder right-click
- folder-background right-click

### Ubuntu package

The `.deb` installs:

- app files under `/opt/sleek-code-browser/`
- CLI launcher at `/usr/bin/sleek`
- desktop file at `/usr/share/applications/sleek-code-browser.desktop`

## GitHub Release Automation

Tagged pushes (`v*`) trigger `.github/workflows/release.yml` to:

1. build Windows installer
2. build Ubuntu `.deb`
3. publish both assets to the tagged GitHub Release
4. mark the release as latest

## Optional One-Command Release Helpers

- `./release.sh`
- `./release.ps1`

These helpers read `VERSION`, commit/tag/push, and use `gh` CLI for release updates.
