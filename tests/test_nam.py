import json
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.nam import (
    apply_gain_db, inspect_nam, peak_dbfs, prepare_nam_input,
    render_capture_chain, scan_nam_models,
)


def write_model(path: Path, *, architecture: str = "SlimmableContainer") -> None:
    path.write_text(
        json.dumps(
            {
                "version": "0.7.0",
                "architecture": architecture,
                "sample_rate": 48000,
                "config": {
                    "submodels": [
                        {"model": {"architecture": "WaveNet", "config": {}}},
                        {"model": {"architecture": "WaveNet", "config": {}}},
                    ]
                },
                "weights": [],
            }
        ),
        encoding="utf-8",
    )


def test_inspects_a2_slimmable_container(tmp_path: Path) -> None:
    path = tmp_path / "amp.nam"
    write_model(path)
    info = inspect_nam(path)
    assert info.path == path.resolve()
    assert (info.version, info.architecture, info.sample_rate, info.submodel_count) == (
        "0.7.0", "SlimmableContainer", 48000, 2
    )


def test_scan_separates_invalid_and_unsupported_models(tmp_path: Path) -> None:
    valid = tmp_path / "valid.nam"
    unsupported = tmp_path / "old.nam"
    broken = tmp_path / "broken.nam"
    write_model(valid)
    write_model(unsupported, architecture="WaveNet")
    broken.write_text("not json", encoding="utf-8")
    models, errors = scan_nam_models(tmp_path)
    assert [model.path for model in models] == [valid.resolve()]
    assert {path for path, _ in errors} == {unsupported, broken}


def test_prepare_nam_input_downmixes_and_resamples() -> None:
    source = AudioBuffer(
        np.array([[1.0, -1.0], [0.5, 0.5]], dtype=np.float32), 24000
    )
    prepared = prepare_nam_input(source, 48000)
    assert prepared.sample_rate == 48000
    assert prepared.samples.shape == (4, 1)
    assert np.isfinite(prepared.samples).all()


def test_capture_gain_and_peak_meter_math() -> None:
    source = AudioBuffer(np.array([[0.25], [-0.5]], dtype=np.float32), 48000)
    boosted = apply_gain_db(source, 6)
    np.testing.assert_allclose(
        boosted.samples[:, 0], source.samples[:, 0] * (10 ** (6 / 20))
    )
    assert peak_dbfs(source) == pytest.approx(-6.0206, abs=0.001)
    with pytest.raises(ValueError, match=r"-24 e \+12"):
        apply_gain_db(source, 13)


def test_nam_only_chain_limits_peak_after_capture_gain(tmp_path: Path) -> None:
    di = tmp_path / "di.wav"
    sf.write(di, [0.1], 48000, subtype="FLOAT")

    class Renderer:
        def render(self, _source, _model):
            return AudioBuffer(np.array([[1.0], [-1.0]], dtype=np.float32), 48000)

    result = render_capture_chain(di, tmp_path / "amp.nam", None, Renderer(), 12)
    assert float(np.max(np.abs(result.samples))) == pytest.approx(0.95)


@pytest.mark.parametrize("filename", ["amp.nan", "amp.json"])
def test_rejects_wrong_extension(tmp_path: Path, filename: str) -> None:
    path = tmp_path / filename
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="extensão .nam"):
        inspect_nam(path)
