import json
from pathlib import Path

import numpy as np
import pytest

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.nam import inspect_nam, prepare_nam_input, scan_nam_models


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


@pytest.mark.parametrize("filename", ["amp.nan", "amp.json"])
def test_rejects_wrong_extension(tmp_path: Path, filename: str) -> None:
    path = tmp_path / filename
    path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="extensão .nam"):
        inspect_nam(path)
