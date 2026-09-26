"""Load bounded WAV files into a consistent frame/channel layout."""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from numpy.typing import NDArray


@dataclass(frozen=True)
class AudioBuffer:
    samples: NDArray[np.float32]
    sample_rate: int


def load_wav(path: Path, *, max_seconds: float = 300) -> AudioBuffer:
    if path.suffix.lower() != ".wav":
        raise ValueError("Selecione um arquivo WAV.")
    with sf.SoundFile(path) as audio_file:
        if audio_file.format not in {"WAV", "WAVEX", "RF64"}:
            raise ValueError("O conteúdo do arquivo não é WAV.")
        if audio_file.channels not in {1, 2}:
            raise ValueError("São aceitos apenas arquivos mono ou estéreo.")
        if not 0 < audio_file.frames <= max_seconds * audio_file.samplerate:
            raise ValueError(f"O WAV deve ter duração entre 0 e {max_seconds:g} segundos.")
        if audio_file.samplerate > 192_000:
            raise ValueError("A taxa máxima nesta etapa é 192 kHz.")
        samples = audio_file.read(dtype="float32", always_2d=True)
        sample_rate = audio_file.samplerate
    if not np.isfinite(samples).all():
        raise ValueError("O WAV contém amostras inválidas (NaN ou infinito).")
    return AudioBuffer(samples, sample_rate)
