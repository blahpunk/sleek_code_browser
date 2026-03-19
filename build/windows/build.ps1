Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$versionFile = Join-Path $repoRoot "VERSION"

if (-not (Test-Path $versionFile)) {
    throw "VERSION file not found at $versionFile"
}

$version = (Get-Content $versionFile -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($version)) {
    throw "VERSION file is empty."
}

$distDir = Join-Path $repoRoot "dist"
$stageDir = Join-Path $repoRoot "installer\windows\build"
$issPath = Join-Path $repoRoot "installer\windows\SleekCodeBrowser.iss"

Push-Location $repoRoot
try {
    Write-Host "Building PyInstaller executable..."
    python -m PyInstaller main.spec --clean

    New-Item -ItemType Directory -Force -Path $stageDir | Out-Null
    Copy-Item (Join-Path $distDir "SleekCodeBrowser.exe") (Join-Path $stageDir "SleekCodeBrowser.exe") -Force
    Copy-Item (Join-Path $repoRoot "icon.ico") (Join-Path $stageDir "icon.ico") -Force

    Write-Host "Building Inno Setup installer..."
    & iscc "/DAppVersion=$version" $issPath
}
finally {
    Pop-Location
}

$installerPath = Join-Path $distDir "SleekCodeBrowser-Setup-$version.exe"
if (-not (Test-Path $installerPath)) {
    throw "Installer build completed but artifact was not found: $installerPath"
}

Write-Host "Windows installer ready: $installerPath"
