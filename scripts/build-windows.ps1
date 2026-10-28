$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$VirtualEnvironment = Join-Path $ProjectRoot ".venv-package"
$Python = Join-Path $VirtualEnvironment "Scripts\python.exe"

if (-not (Test-Path $Python)) {
    py -3.12 -m venv $VirtualEnvironment
}

& $Python -m pip install --upgrade pip
& $Python -m pip install -e ".[dev,package]"
& $Python -m pytest -q
& "$PSScriptRoot\build-nam-runtime.ps1"
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --name "AuditionManager" `
    --paths "src" `
    --collect-all "sounddevice" `
    --collect-all "soundfile" `
    "src\audition_manager\__main__.py"

$Bundle = Join-Path $ProjectRoot "dist\AuditionManager"
Copy-Item "LICENSE" $Bundle -Force
Copy-Item "README.md" $Bundle -Force
$NamBundle = Join-Path $Bundle "build\nam-runtime"
New-Item -ItemType Directory -Force $NamBundle | Out-Null
Copy-Item "build\nam-runtime\nam-render.exe" $NamBundle -Force

$Archive = Join-Path $ProjectRoot "dist\AuditionManager-Windows-x64.zip"
if (Test-Path $Archive) {
    Remove-Item $Archive -Force
}
Compress-Archive -Path $Bundle -DestinationPath $Archive

Write-Host ""
Write-Host "Executavel: $Bundle\AuditionManager.exe"
Write-Host "Pacote:     $Archive"
