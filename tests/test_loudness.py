from pathlib import Path

import numpy as np
import pytest

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.loudness import (
    chain_measurement_key, measure_integrated_loudness,
)


def sine(amplitude: float, seconds: float = 1.0) -> AudioBuffer:
    rate = 48_000
    time = np.arange(round(rate * seconds), dtype=np.float64) / rate
    samples = amplitude * np.sin(2 * np.pi * 440 * time)
    return AudioBuffer(samples.astype(np.float32)[:, None], rate)


def test_integrated_loudness_tracks_a_six_db_gain_change() -> None:
    quiet = measure_integrated_loudness(sine(0.1))
    loud = measure_integrated_loudness(sine(0.1 * (10 ** (6 / 20))))
    assert loud.loudness_lufs - quiet.loudness_lufs == pytest.approx(6.0, abs=0.05)
    assert quiet.loudness_lufs + quiet.compensation_db == pytest.approx(
        -18.0, abs=0.001
    )


@pytest.mark.parametrize(
    "audio",
    [
        AudioBuffer(np.zeros((48_000, 1), dtype=np.float32), 48_000),
        sine(0.1, seconds=0.1),
    ],
)
def test_silence_and_short_audio_are_not_measurable(audio: AudioBuffer) -> None:
    with pytest.raises(ValueError):
        measure_integrated_loudness(audio)


def test_chain_key_changes_with_files_and_quality(tmp_path: Path) -> None:
    di = tmp_path / "di.wav"
    capture = tmp_path / "amp.nam"
    ir = tmp_path / "cab.wav"
    for path, content in ((di, b"di"), (capture, b"nam"), (ir, b"ir")):
        path.write_bytes(content)

    full = chain_measurement_key(di, capture, ir, "full")
    assert full == chain_measurement_key(di, capture, ir, "full")
    assert full != chain_measurement_key(di, capture, ir, "lite")
    assert full != chain_measurement_key(di, capture, None, "full")
    ir.write_bytes(b"changed-ir")
    assert full != chain_measurement_key(di, capture, ir, "full")
