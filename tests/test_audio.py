from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audition_manager.audio.files import AudioBuffer, load_wav
from audition_manager.audio.ir_processor import convolve_ir, render_files
from audition_manager.library.scanner import inspect_wavs, scan_wavs


def buffer(values: list[list[float]], rate: int = 48000) -> AudioBuffer:
    return AudioBuffer(np.array(values, dtype=np.float32), rate)


def test_convolution_preserves_tail_and_channel_independence() -> None:
    result = convolve_ir(buffer([[0.1, 0.2], [0.2, 0.1]]), buffer([[1], [0.5]]))
    np.testing.assert_allclose(result.samples, [[0.1, 0.2], [0.25, 0.2], [0.1, 0.05]], atol=1e-7)


def test_mono_source_with_stereo_ir() -> None:
    result = convolve_ir(buffer([[0.2], [0.1]]), buffer([[1, 0.5]]))
    np.testing.assert_allclose(result.samples, [[0.2, 0.1], [0.1, 0.05]], atol=1e-7)


def test_peak_attenuation_preserves_relative_amplitudes() -> None:
    result = convolve_ir(buffer([[0.8], [0.4]]), buffer([[2]]))
    np.testing.assert_allclose(result.samples, [[0.95], [0.475]], atol=1e-7)


def test_resampling_uses_source_rate_and_expected_length() -> None:
    result = convolve_ir(buffer([[0.1]]), buffer([[1], [0]], rate=24000))
    assert result.sample_rate == 48000
    assert result.samples.shape == (4, 1)
    assert np.isfinite(result.samples).all()


def test_scan_and_render_real_wavs(tmp_path: Path) -> None:
    di = tmp_path / "di.wav"
    folder = tmp_path / "irs"
    folder.mkdir()
    ir = folder / "identity.WAV"
    sf.write(di, [0.1, -0.2, 0.3], 48000, subtype="FLOAT")
    sf.write(ir, [1.0], 48000, subtype="FLOAT")
    (folder / "ignored.txt").write_text("ignored")
    assert scan_wavs(folder) == [ir]
    result = render_files(di, ir)
    np.testing.assert_allclose(result.samples[:, 0], [0.1, -0.2, 0.3], atol=1e-7)


@pytest.mark.parametrize("kind", ["empty", "long", "multichannel", "nan", "corrupt"])
def test_invalid_wavs_are_rejected(tmp_path: Path, kind: str) -> None:
    path = tmp_path / "invalid.wav"
    samples = {
        "empty": np.zeros(0), "long": np.zeros(101),
        "multichannel": np.zeros((4, 3)), "nan": np.array([np.nan]),
    }
    if kind == "corrupt":
        path.write_text("not a WAV")
    else:
        sf.write(path, samples[kind], 100, subtype="FLOAT")
    with pytest.raises((ValueError, sf.LibsndfileError)):
        load_wav(path, max_seconds=1)


def test_recursive_scan_is_case_insensitive_and_sorted(tmp_path: Path) -> None:
    nested = tmp_path / "cab"
    nested.mkdir()
    first = nested / "A.WAV"
    second = nested / "b.wav"
    first.touch()
    second.touch()
    assert scan_wavs(tmp_path) == [first, second]


def test_inspection_returns_metadata_and_separates_invalid_wavs(tmp_path: Path) -> None:
    valid = tmp_path / "cab.wav"
    invalid = tmp_path / "broken.wav"
    sf.write(valid, np.zeros((8, 2), dtype=np.float32), 44100)
    invalid.write_text("not audio")
    items, errors = inspect_wavs([valid, invalid])
    assert len(items) == 1
    assert items[0].path == valid.resolve()
    assert (items[0].sample_rate, items[0].channels) == (44100, 2)
    assert errors[0][0] == invalid
