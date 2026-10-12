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
        self.channels = kwargs.get("channels", 1)
        self.samplerate = kwargs.get("samplerate", 48000)
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
        query_devices=Mock(), query_hostapis=Mock(),
        OutputStream=Mock(side_effect=FakeStream),
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



def test_replace_same_format_keeps_stream_cursor_and_pause(backend) -> None:
    output = AudioOutput()
    original = AudioBuffer(np.full((10, 1), 0.1, dtype=np.float32), 48000)
    replacement = AudioBuffer(np.full((10, 1), 0.5, dtype=np.float32), 48000)
    output.play(original)
    stream = output._stream
    block = np.empty((2, 1), dtype=np.float32)
    stream.options["callback"](block, 2, None, None)
    output.pause()
    before = output.transport.snapshot()
    output.replace(replacement)
    assert output.transport.snapshot() == before
    assert output._stream is stream
    output.play()
    stream.options["callback"](block, 2, None, None)
    np.testing.assert_allclose(block[:, 0], [0.1, 0.1 * 8 / 9 + 0.5 / 9])
    assert backend.OutputStream.call_count == 1


def test_channel_change_preserves_paused_position(backend) -> None:
    output = AudioOutput()
    output.play(AudioBuffer(np.zeros((10, 1), dtype=np.float32), 48000))
    old = output._stream
    old.options["callback"](np.zeros((2, 1), dtype=np.float32), 2, None, None)
    output.pause()
    before = output.transport.snapshot()
    output.replace(AudioBuffer(np.zeros((10, 2), dtype=np.float32), 48000))
    assert output.transport.snapshot() == before
    assert old.closed
    assert not output._stream.active
    assert output._stream.channels == 2


def test_lists_only_output_devices_with_host_api(backend) -> None:
    backend.query_devices.return_value = [
        {"name": "Input", "max_output_channels": 0, "hostapi": 0},
        {"name": "Speakers", "max_output_channels": 2, "hostapi": 1},
    ]
    backend.query_hostapis.return_value = {"name": "WASAPI"}
    devices = AudioOutput().list_devices()
    assert [(item.index, item.name, item.host_api) for item in devices] == [
        (1, "Speakers", "WASAPI")
    ]
    backend.query_hostapis.assert_called_once_with(1)


def test_gain_attenuates_callback_without_changing_transport_audio(backend) -> None:
    output = AudioOutput()
    audio = AudioBuffer(np.full((4, 1), 0.8, dtype=np.float32), 48000)
    output.play(audio, loop=True)
    output.set_gain_db(-6)
    block = np.empty((2, 1), dtype=np.float32)
    output._stream.options["callback"](block, 2, None, None)
    np.testing.assert_allclose(block, 0.8 * 10 ** (-6 / 20), rtol=1e-6)
    np.testing.assert_allclose(audio.samples, 0.8)
    with pytest.raises(ValueError):
        output.set_gain_db(1)


def test_device_change_reopens_stream_and_preserves_playing_cursor(backend) -> None:
    output = AudioOutput()
    audio = AudioBuffer(np.full((20, 1), 0.2, dtype=np.float32), 48000)
    output.play(audio, loop=True)
    old = output._stream
    old.options["callback"](np.empty((4, 1), dtype=np.float32), 4, None, None)
    before = output.transport.snapshot()
    output.set_device(7)
    assert old.closed
    assert output.device == 7
    assert output._stream.options["device"] == 7
    assert output._stream.active
    assert output.transport.snapshot() == before
