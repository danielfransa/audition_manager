import sys
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.output import AudioOutput
from audition_manager.audio.transport import PlaybackState


class FakeStream:
    def __init__(self, **kwargs) -> None:
        self.options = kwargs
        self.active = False
        self.closed = False

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False

    abort = stop

    def close(self) -> None:
        self.active = False
        self.closed = True


@pytest.fixture
def backend(monkeypatch):
    backend = SimpleNamespace(
        PortAudioError=OSError, CallbackStop=StopIteration,
        query_devices=Mock(), OutputStream=Mock(side_effect=FakeStream),
    )
    monkeypatch.setitem(sys.modules, "sounddevice", backend)
    return backend


def test_missing_wsl_output_explains_bridge_and_does_not_open(backend, monkeypatch) -> None:
    backend.query_devices.side_effect = OSError("Error querying device -1")
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("PULSE_SERVER", "unix:/mnt/wslg/PulseServer")
    audio = AudioBuffer(np.zeros((4, 1), dtype=np.float32), 48000)
    with pytest.raises(RuntimeError, match="alsa-plugins e pulseaudio-alsa"):
        AudioOutput().play(audio)
    backend.OutputStream.assert_not_called()


def test_stream_is_reused_for_pause_resume_stop_and_closed(backend) -> None:
    audio = AudioBuffer(np.array([[0.1], [0.2], [0.3]], dtype=np.float32), 44100)
    output = AudioOutput()
    output.play(audio, loop=True)
    stream = output._stream
    assert stream.options["samplerate"] == 44100
    assert stream.options["channels"] == 1
    block = np.empty((2, 1), dtype=np.float32)
    stream.options["callback"](block, 2, None, None)
    output.pause()
    assert not stream.active
    assert output.transport.snapshot()[0] == PlaybackState.PAUSED
    output.play()
    stream.options["callback"](block, 2, None, None)
    np.testing.assert_allclose(block[:, 0], [0.3, 0.1])
    assert backend.OutputStream.call_count == 1
    output.stop()
    assert output.transport.snapshot()[1] == 0
    output.close()
    assert stream.closed
    assert output.transport.snapshot()[0] == PlaybackState.EMPTY


def test_last_block_is_delivered_before_callback_stop(backend) -> None:
    output = AudioOutput()
    output.play(AudioBuffer(np.array([[0.2]], dtype=np.float32), 48000))
    block = np.empty((3, 1), dtype=np.float32)
    with pytest.raises(StopIteration):
        output._stream.options["callback"](block, 3, None, None)
    np.testing.assert_allclose(block[:, 0], [0.2, 0, 0])


def test_start_failure_leaves_retriable_paused_state(backend) -> None:
    stream = FakeStream()
    stream.start = Mock(side_effect=OSError("Device unavailable"))
    backend.OutputStream.side_effect = None
    backend.OutputStream.return_value = stream
    output = AudioOutput()
    with pytest.raises(OSError):
        output.play(AudioBuffer(np.zeros((8, 1), dtype=np.float32), 48000))
    assert output.transport.snapshot()[0] == PlaybackState.PAUSED
    output.close()
    assert stream.closed

