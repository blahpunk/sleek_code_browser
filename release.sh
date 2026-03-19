#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

version="$(tr -d '[:space:]' < VERSION)"
if [[ -z "$version" ]]; then
  echo "VERSION is empty." >&2
  exit 1
fi

tag="v${version}"
win_asset="$repo_root/dist/SleekCodeBrowser-Setup-${version}.exe"
deb_asset="$repo_root/dist/sleek-code-browser_${version}_amd64.deb"

if [[ -n "$(git status --porcelain)" ]]; then
  git add .
  git commit -m "Release ${tag}" || true
fi

git push origin main

if ! git rev-parse "$tag" >/dev/null 2>&1; then
  git tag "$tag"
fi
git push origin "$tag"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found; skipping direct release creation."
  exit 0
fi

release_assets=()
[[ -f "$win_asset" ]] && release_assets+=("$win_asset")
[[ -f "$deb_asset" ]] && release_assets+=("$deb_asset")

if gh release view "$tag" >/dev/null 2>&1; then
  if [[ ${#release_assets[@]} -gt 0 ]]; then
    gh release upload "$tag" "${release_assets[@]}" --clobber
  fi
  gh release edit "$tag" --title "Sleek Code Browser ${tag}" --latest
else
  if [[ ${#release_assets[@]} -gt 0 ]]; then
    gh release create "$tag" \
      --title "Sleek Code Browser ${tag}" \
      --notes "Release ${tag}" \
      "${release_assets[@]}"
  else
    gh release create "$tag" \
      --title "Sleek Code Browser ${tag}" \
      --notes "Release ${tag}"
  fi
  gh release edit "$tag" --latest
fi
