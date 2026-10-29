$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SourceDir = Join-Path $ProjectRoot "build\nam-runtime-src"
$OutputDir = Join-Path $ProjectRoot "build\nam-runtime"
$CoreCommit = "0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842"

if (-not (Test-Path (Join-Path $SourceDir ".git"))) {
    git clone https://github.com/sdatkinson/NeuralAmpModelerCore.git $SourceDir
    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao clonar NeuralAmpModelerCore (codigo $LASTEXITCODE)."
    }
}
git -C $SourceDir fetch origin $CoreCommit
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao baixar o commit do runtime NAM (codigo $LASTEXITCODE)."
}
git -C $SourceDir checkout --detach $CoreCommit
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao selecionar o commit do runtime NAM (codigo $LASTEXITCODE)."
}
git -C $SourceDir config submodule.Dependencies/eigen.url https://eigen.googlesource.com/mirror
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao configurar o submodulo Eigen (codigo $LASTEXITCODE)."
}
git -C $SourceDir submodule update --init --recursive
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao baixar os submodulos do runtime NAM (codigo $LASTEXITCODE)."
}

# This pinned upstream commit applies the GCC/Clang flag -Wno-error to three
# source files even when CMake generates an MSVC project. MSVC rewrites it as
# /Wno-error and aborts with D8021. Use the equivalent MSVC flag reproducibly.
$ToolsCMake = Join-Path $SourceDir "tools\CMakeLists.txt"
$CMakeText = [System.IO.File]::ReadAllText($ToolsCMake)
$GnuFlagCount = ([regex]::Matches($CMakeText, 'COMPILE_FLAGS "-Wno-error"')).Count
$MsvcFlagCount = ([regex]::Matches($CMakeText, 'COMPILE_FLAGS "/WX-"')).Count
if ($GnuFlagCount -eq 3) {
    $CMakeText = $CMakeText.Replace(
        'COMPILE_FLAGS "-Wno-error"', 'COMPILE_FLAGS "/WX-"'
    )
    [System.IO.File]::WriteAllText(
        $ToolsCMake, $CMakeText, [System.Text.UTF8Encoding]::new($false)
    )
} elseif ($MsvcFlagCount -ne 3) {
    throw "Nao foi possivel aplicar a correcao MSVC no CMake do runtime NAM."
}

$BuildDir = Join-Path $SourceDir "cmake-build"
cmake -S $SourceDir -B $BuildDir -G "Visual Studio 17 2022" -A x64 -DNAM_ENABLE_A2_FAST=ON
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao configurar o runtime NAM com CMake (codigo $LASTEXITCODE)."
}
cmake --build $BuildDir --config Release --target render --parallel
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao compilar o runtime NAM (codigo $LASTEXITCODE)."
}
New-Item -ItemType Directory -Force $OutputDir | Out-Null
$Renderer = Join-Path $BuildDir "tools\Release\render.exe"
if (-not (Test-Path $Renderer)) {
    throw "CMake terminou sem produzir $Renderer."
}
Copy-Item $Renderer (Join-Path $OutputDir "nam-render.exe") -Force
Write-Host "Runtime NAM criado em $OutputDir\nam-render.exe"
