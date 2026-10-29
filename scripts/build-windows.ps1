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
Copy-Item "docs\windows-portable.md" (Join-Path $Bundle "README.md") -Force
$NamBundle = Join-Path $Bundle "build\nam-runtime"
New-Item -ItemType Directory -Force $NamBundle | Out-Null
Copy-Item "build\nam-runtime\nam-render.exe" $NamBundle -Force

# Package only samples tracked by Git. This deliberately excludes personal NAM
# captures or other local files that happen to be under samples/.
$TrackedSamples = @(git ls-files -- samples)
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel listar os samples versionados (codigo $LASTEXITCODE)."
}
foreach ($RelativePath in $TrackedSamples) {
    $Source = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path $Source -PathType Leaf)) {
        continue
    }
    $Destination = Join-Path $Bundle $RelativePath
    New-Item -ItemType Directory -Force (Split-Path -Parent $Destination) | Out-Null
    Copy-Item $Source $Destination -Force
}

$Executable = Join-Path $Bundle "AuditionManager.exe"
& $Executable --packaging-smoke-test
if ($LASTEXITCODE -ne 0) {
    throw "O autoteste do pacote retornou o codigo $LASTEXITCODE."
}

$Archive = Join-Path $ProjectRoot "dist\AuditionManager-Windows-x64.zip"
if (Test-Path $Archive) {
    Remove-Item $Archive -Force
}
Compress-Archive -Path $Bundle -DestinationPath $Archive

Write-Host ""
Write-Host "Executavel: $Executable"
Write-Host "Pacote:     $Archive"
