"""Offline convolution, independent of the UI and output device."""

from math import gcd
from pathlib import Path

import numpy as np
from scipy.signal import fftconvolve, resample_poly

from audition_manager.audio.files import AudioBuffer, load_wav


def convolve_ir(source: AudioBuffer, impulse: AudioBuffer) -> AudioBuffer:
    kernel = impulse.samples
    if impulse.sample_rate != source.sample_rate:
        divisor = gcd(impulse.sample_rate, source.sample_rate)
        kernel = resample_poly(
            kernel,
            source.sample_rate // divisor,
            impulse.sample_rate // divisor,
            axis=0,
        )
    channels = max(source.samples.shape[1], kernel.shape[1])
    # Mono broadcasts to stereo; stereo pairs are convolved independently.
    signal = np.broadcast_to(source.samples, (len(source.samples), channels))
    kernel = np.broadcast_to(kernel, (len(kernel), channels))
    result = fftconvolve(signal, kernel, mode="full", axes=0)
    if not np.isfinite(result).all():
        raise ValueError("O processamento produziu amostras inválidas.")
    return limit_peak(AudioBuffer(np.ascontiguousarray(result, dtype=np.float32), source.sample_rate))


def limit_peak(audio: AudioBuffer) -> AudioBuffer:
    """Attenuate only when required; never amplify quiet material."""
    peak = float(np.max(np.abs(audio.samples)))
    if peak <= 0.95:
        return audio
    return AudioBuffer(
        np.ascontiguousarray(audio.samples * (0.95 / peak), dtype=np.float32),
        audio.sample_rate,
    )


def render_files(di_path: Path, ir_path: Path) -> AudioBuffer:
    source = load_wav(di_path)
    impulse = load_wav(ir_path, max_seconds=2)
    return convolve_ir(source, impulse)
