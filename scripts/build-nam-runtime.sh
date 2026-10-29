#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$project_root/build/nam-runtime-src"
output_dir="$project_root/build/nam-runtime"
core_commit="0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842"

command -v git >/dev/null || { echo "git não encontrado." >&2; exit 1; }
command -v cmake >/dev/null || { echo "cmake não encontrado." >&2; exit 1; }

if [[ ! -d "$source_dir/.git" ]]; then
    git clone https://github.com/sdatkinson/NeuralAmpModelerCore.git "$source_dir"
fi
git -C "$source_dir" fetch origin "$core_commit"
git -C "$source_dir" checkout --detach "$core_commit"
# O upstream aponta Eigen para GitLab. O espelho oficial mantido pelo projeto
# Eigen no Google é usado quando o GitLab não está disponível.
git -C "$source_dir" config submodule.Dependencies/eigen.url https://eigen.googlesource.com/mirror
git -C "$source_dir" submodule update --init --recursive

cmake -S "$source_dir" -B "$source_dir/cmake-build" -DCMAKE_BUILD_TYPE=Release -DNAM_ENABLE_A2_FAST=ON
cmake --build "$source_dir/cmake-build" --config Release --target render --parallel
mkdir -p "$output_dir"
cp "$source_dir/cmake-build/tools/render" "$output_dir/nam-render"
echo "Runtime NAM criado em $output_dir/nam-render"
