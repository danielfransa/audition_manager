"""Integrated-loudness measurement and bounded comparison gain."""

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

import pyloudnorm as pyln

from audition_manager.audio.files import AudioBuffer

ALGORITHM_VERSION = "bs1770-v1"
TARGET_LOUDNESS_LUFS = -18.0
MIN_COMPENSATION_DB = -24.0
MAX_COMPENSATION_DB = 12.0


@dataclass(frozen=True)
class LoudnessMeasurement:
    loudness_lufs: float
    compensation_db: float
    method: str = ALGORITHM_VERSION


def compensation_db(loudness: float | None) -> float:
    if loudness is None or not isfinite(loudness):
        return 0.0
    return max(
        MIN_COMPENSATION_DB,
        min(MAX_COMPENSATION_DB, TARGET_LOUDNESS_LUFS - loudness),
    )


def measure_integrated_loudness(audio: AudioBuffer) -> LoudnessMeasurement:
    minimum_frames = round(0.4 * audio.sample_rate)
    if len(audio.samples) < minimum_frames:
        raise ValueError("O áudio é curto demais para medir loudness integrado.")
    loudness = float(
        pyln.Meter(audio.sample_rate, block_size=0.400).integrated_loudness(
            audio.samples
        )
    )
    if not isfinite(loudness):
        raise ValueError("O áudio não possui loudness integrado mensurável.")
    return LoudnessMeasurement(loudness, compensation_db(loudness))


def chain_measurement_key(
    di_path: Path,
    capture_path: Path | None,
    ir_path: Path | None,
    quality: str,
) -> str:
    def identity(path: Path | None) -> dict[str, object] | None:
        if path is None:
            return None
        resolved = path.resolve()
        stat = resolved.stat()
        return {
            "path": str(resolved),
            "mtime_ns": stat.st_mtime_ns,
            "ctime_ns": stat.st_ctime_ns,
            "size": stat.st_size,
        }

    payload = {
        "algorithm": ALGORITHM_VERSION,
        "target_lufs": TARGET_LOUDNESS_LUFS,
        "di": identity(di_path),
        "capture": identity(capture_path),
        "ir": identity(ir_path),
        "quality": quality if capture_path is not None else None,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return sha256(encoded).hexdigest()
