$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SourceDir = Join-Path $ProjectRoot "build\nam-runtime-src"
$OutputDir = Join-Path $ProjectRoot "build\nam-runtime"
$CoreCommit = "0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842"

if (-not (Test-Path (Join-Path $SourceDir ".git"))) {
    git clone https://github.com/sdatkinson/NeuralAmpModelerCore.git $SourceDir
}
git -C $SourceDir fetch origin $CoreCommit
git -C $SourceDir checkout --detach $CoreCommit
git -C $SourceDir config submodule.Dependencies/eigen.url https://eigen.googlesource.com/mirror
git -C $SourceDir submodule update --init --recursive

$BuildDir = Join-Path $SourceDir "cmake-build"
cmake -S $SourceDir -B $BuildDir -G "Visual Studio 17 2022" -A x64 -DNAM_ENABLE_A2_FAST=ON
cmake --build $BuildDir --config Release --target render --parallel
New-Item -ItemType Directory -Force $OutputDir | Out-Null
Copy-Item (Join-Path $BuildDir "tools\Release\render.exe") (Join-Path $OutputDir "nam-render.exe") -Force
Write-Host "Runtime NAM criado em $OutputDir\nam-render.exe"
