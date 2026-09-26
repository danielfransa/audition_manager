from unittest.mock import Mock

import numpy as np
import soundfile as sf

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.render_cache import RenderCache


def test_cache_hits_invalidates_changed_files_and_evicts_lru(tmp_path) -> None:
    di = tmp_path / "di.wav"
    di.touch()
    paths = [tmp_path / f"{index}.wav" for index in range(3)]
    for path in paths:
        path.touch()
    audio = AudioBuffer(np.zeros((2, 1), dtype=np.float32), 48000)
    renderer = Mock(return_value=audio)
    cache = RenderCache(max_bytes=16, max_entries=2)
    cache.render(di, paths[0], renderer)
    cache.render(di, paths[1], renderer)
    cache.render(di, paths[0], renderer)
    assert renderer.call_count == 2
    cache.render(di, paths[2], renderer)
    cache.render(di, paths[1], renderer)
    assert renderer.call_count == 4
    assert cache.bytes_used == 16
    paths[1].write_bytes(b"changed")
    cache.render(di, paths[1], renderer)
    assert renderer.call_count == 5
    di.write_bytes(b"new source")
    cache.render(di, paths[1], renderer)
    assert renderer.call_count == 6


def test_oversized_result_is_not_retained(tmp_path) -> None:
    path = tmp_path / "audio.wav"
    path.touch()
    renderer = Mock(return_value=AudioBuffer(np.zeros((8, 1), dtype=np.float32), 48000))
    cache = RenderCache(max_bytes=4)
    cache.render(path, path, renderer)
    cache.render(path, path, renderer)
    assert renderer.call_count == 2
    assert cache.bytes_used == 0


def test_bypass_does_not_convolve_and_keeps_source_shape(tmp_path) -> None:
    path = tmp_path / "di.wav"
    sf.write(path, [0.2, -0.4, 0.1], 48000, subtype="FLOAT")
    renderer = Mock()
    cache = RenderCache()
    audio = cache.render(path, None, renderer)
    renderer.assert_not_called()
    np.testing.assert_allclose(audio.samples[:, 0], [0.2, -0.4, 0.1])
    assert audio.sample_rate == 48000
    assert cache.render(path, None, renderer) is audio


def test_bypass_attenuates_overload_without_clipping(tmp_path) -> None:
    path = tmp_path / "di.wav"
    sf.write(path, [2.0, -1.0], 48000, subtype="FLOAT")
    audio = RenderCache().render(path, None, Mock())
    np.testing.assert_allclose(audio.samples[:, 0], [0.95, -0.475])
