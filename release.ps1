Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path $PSScriptRoot
Set-Location $repoRoot

$version = (Get-Content (Join-Path $repoRoot "VERSION") -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($version)) {
    throw "VERSION is empty."
}

$tag = "v$version"
$windowsAsset = Join-Path $repoRoot "dist\SleekCodeBrowser-Setup-$version.exe"
$ubuntuAsset = Join-Path $repoRoot "dist\sleek-code-browser_${version}_amd64.deb"

if ((git status --porcelain).Trim().Length -gt 0) {
    git add .
    try {
        git commit -m "Release $tag"
    }
    catch {
        Write-Host "No commit created (possibly no staged diff after add)."
    }
}

git push origin main

try {
    git rev-parse $tag | Out-Null
}
catch {
    git tag $tag
}

git push origin $tag

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "gh CLI not found; skipping direct release creation."
    exit 0
}

$assets = @()
if (Test-Path $windowsAsset) { $assets += $windowsAsset }
if (Test-Path $ubuntuAsset) { $assets += $ubuntuAsset }

$releaseExists = $true
try {
    gh release view $tag | Out-Null
}
catch {
    $releaseExists = $false
}

if ($releaseExists) {
    if ($assets.Count -gt 0) {
        gh release upload $tag $assets --clobber
    }
    gh release edit $tag --title "Sleek Code Browser $tag" --latest
}
else {
    if ($assets.Count -gt 0) {
        gh release create $tag --title "Sleek Code Browser $tag" --notes "Release $tag" $assets
    }
    else {
        gh release create $tag --title "Sleek Code Browser $tag" --notes "Release $tag"
    }
    gh release edit $tag --latest
}
