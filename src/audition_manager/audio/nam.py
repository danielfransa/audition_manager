"""NAM A2 inspection and offline rendering through NeuralAmpModelerCore."""

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from math import gcd
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from audition_manager.audio.files import AudioBuffer, load_wav
from audition_manager.audio.ir_processor import convolve_ir


@dataclass(frozen=True)
class NamModelInfo:
    path: Path
    version: str
    architecture: str
    sample_rate: int
    submodel_count: int


def inspect_nam(path: Path) -> NamModelInfo:
    if path.suffix.lower() != ".nam":
        raise ValueError("A captura deve usar a extensão .nam.")
    if path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("A captura NAM excede o limite de 64 MiB.")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("O arquivo NAM não contém JSON válido.") from error
    if not isinstance(payload, dict):
        raise ValueError("A raiz do arquivo NAM deve ser um objeto JSON.")
    version = payload.get("version")
    architecture = payload.get("architecture")
    sample_rate = payload.get("sample_rate", 48_000)
    if not isinstance(version, str) or not version:
        raise ValueError("A captura NAM não informa uma versão válida.")
    if architecture != "SlimmableContainer":
        raise ValueError(
            f"Arquitetura NAM ainda não suportada: {architecture or 'ausente'}."
        )
    if not isinstance(sample_rate, (int, float)) or isinstance(sample_rate, bool):
        raise ValueError("A captura NAM não informa uma taxa válida.")
    rounded_rate = round(sample_rate)
    if rounded_rate <= 0 or abs(sample_rate - rounded_rate) > 0.01:
        raise ValueError("A captura NAM não informa uma taxa inteira válida.")
    config = payload.get("config")
    submodels = config.get("submodels") if isinstance(config, dict) else None
    if not isinstance(submodels, list) or not submodels:
        raise ValueError("O SlimmableContainer não contém submodelos.")
    for submodel in submodels:
        model = submodel.get("model") if isinstance(submodel, dict) else None
        if not isinstance(model, dict) or model.get("architecture") != "WaveNet":
            raise ValueError("O container possui um submodelo incompatível.")
    return NamModelInfo(
        path.resolve(), version, architecture, rounded_rate, len(submodels)
    )


def scan_nam_models(root: Path) -> tuple[list[NamModelInfo], list[tuple[Path, str]]]:
    models: list[NamModelInfo] = []
    errors: list[tuple[Path, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: str(item).casefold()):
        if not path.is_file() or path.suffix.lower() != ".nam":
            continue
        try:
            models.append(inspect_nam(path))
        except (OSError, ValueError) as error:
            errors.append((path, str(error)))
    return models, errors


class NamRenderer:
    def __init__(self, executable: Path | None = None, timeout_seconds: int = 180) -> None:
        self.executable = executable or self._default_executable()
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _default_executable() -> Path:
        override = os.environ.get("AUDITION_MANAGER_NAM_RENDERER")
        if override:
            return Path(override).expanduser()
        name = "nam-render.exe" if os.name == "nt" else "nam-render"
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / "build" / "nam-runtime" / name
        project_root = Path(__file__).resolve().parents[3]
        return project_root / "build" / "nam-runtime" / name

    def render(self, source: AudioBuffer, model_path: Path) -> AudioBuffer:
        model = inspect_nam(model_path)
        if not self.executable.is_file():
            raise RuntimeError(
                "Runtime NAM não encontrado. Execute scripts/build-nam-runtime.sh "
                "no Linux ou scripts\\build-nam-runtime.ps1 no Windows."
            )
        prepared = prepare_nam_input(source, model.sample_rate)
        with tempfile.TemporaryDirectory(prefix="audition-manager-nam-") as directory:
            temporary = Path(directory)
            input_path = temporary / "input.wav"
            output_path = temporary / "output.wav"
            sf.write(input_path, prepared.samples, prepared.sample_rate, subtype="FLOAT")
            try:
                result = subprocess.run(
                    [
                        str(self.executable), "--slim", "1.0", str(model.path),
                        str(input_path), str(output_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as error:
                raise RuntimeError(f"Falha ao executar o runtime NAM: {error}") from error
            if result.returncode != 0:
                detail = result.stderr.strip() or result.stdout.strip()
                raise RuntimeError(f"O runtime NAM recusou a captura.\n\n{detail}")
            return load_wav(output_path)


def prepare_nam_input(source: AudioBuffer, sample_rate: int) -> AudioBuffer:
    samples = np.mean(source.samples, axis=1, keepdims=True, dtype=np.float32)
    if source.sample_rate != sample_rate:
        divisor = gcd(source.sample_rate, sample_rate)
        samples = resample_poly(
            samples,
            sample_rate // divisor,
            source.sample_rate // divisor,
            axis=0,
        )
    return AudioBuffer(np.ascontiguousarray(samples, dtype=np.float32), sample_rate)


def render_capture_chain(
    di_path: Path, capture_path: Path, ir_path: Path | None, renderer: NamRenderer
) -> AudioBuffer:
    source = load_wav(di_path)
    captured = renderer.render(source, capture_path)
    if ir_path is None:
        return captured
    impulse = load_wav(ir_path, max_seconds=2)
    return convolve_ir(captured, impulse)
