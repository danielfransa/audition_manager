import numpy as np

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.transport import PlaybackState, PlaybackTransport


def make_transport() -> PlaybackTransport:
    transport = PlaybackTransport()
    transport.load(AudioBuffer(np.array([[0.1], [0.2], [0.3]], dtype=np.float32), 10))
    transport.play()
    return transport


def test_pause_resume_preserves_next_frame_and_stop_rewinds() -> None:
    transport = make_transport()
    block = np.empty((1, 1), dtype=np.float32)
    transport.fill(block)
    transport.pause()
    position = transport.snapshot()[1]
    transport.fill(block)
    np.testing.assert_array_equal(block, 0)
    assert transport.snapshot() == (PlaybackState.PAUSED, position, 0.3)
    transport.play()
    transport.fill(block)
    np.testing.assert_allclose(block, [[0.2]])
    transport.stop()
    assert transport.snapshot() == (PlaybackState.STOPPED, 0, 0.3)
    transport.play()
    transport.fill(block)
    np.testing.assert_allclose(block, [[0.1]])


def test_partial_final_block_is_zero_padded_and_replay_starts_at_zero() -> None:
    transport = make_transport()
    block = np.empty((5, 1), dtype=np.float32)
    assert transport.fill(block)
    np.testing.assert_allclose(block[:, 0], [0.1, 0.2, 0.3, 0, 0])
    assert transport.snapshot() == (PlaybackState.FINISHED, 0.3, 0.3)
    transport.play()
    assert transport.snapshot() == (PlaybackState.PLAYING, 0, 0.3)


def test_loop_wraps_multiple_times_within_one_block_and_can_be_disabled() -> None:
    transport = make_transport()
    transport.set_loop(True)
    block = np.empty((8, 1), dtype=np.float32)
    assert not transport.fill(block)
    np.testing.assert_allclose(block[:, 0], [0.1, 0.2, 0.3, 0.1, 0.2, 0.3, 0.1, 0.2])
    transport.set_loop(False)
    assert transport.fill(block)
    np.testing.assert_allclose(block[:, 0], [0.3, 0, 0, 0, 0, 0, 0, 0])


def test_exact_boundary_finishes_and_clear_releases_audio() -> None:
    transport = make_transport()
    assert transport.fill(np.empty((3, 1), dtype=np.float32))
    transport.clear()
    assert transport.snapshot() == (PlaybackState.EMPTY, 0, 0)


def test_replace_crossfades_for_ten_milliseconds_and_keeps_position() -> None:
    transport = PlaybackTransport()
    transport.load(AudioBuffer(np.ones((30, 1), dtype=np.float32), 1000))
    transport.play()
    transport.fill(np.empty((5, 1), dtype=np.float32))
    transport.replace(AudioBuffer(np.zeros((30, 1), dtype=np.float32), 1000))
    block = np.empty((12, 1), dtype=np.float32)
    transport.fill(block)
    np.testing.assert_allclose(
        block[:, 0], [1, 8 / 9, 7 / 9, 6 / 9, 5 / 9, 4 / 9, 3 / 9, 2 / 9, 1 / 9, 0, 0, 0]
    )
    assert transport.snapshot()[1] == 0.017


def test_paused_replace_defers_crossfade_and_stop_discards_it() -> None:
    transport = PlaybackTransport()
    transport.load(AudioBuffer(np.ones((30, 1), dtype=np.float32), 1000))
    transport.play()
    transport.pause()
    transport.replace(AudioBuffer(np.zeros((30, 1), dtype=np.float32), 1000))
    paused = np.empty((2, 1), dtype=np.float32)
    transport.fill(paused)
    np.testing.assert_array_equal(paused, 0)
    transport.play()
    transport.fill(paused)
    assert paused[0, 0] == 1
    transport.stop()
    transport.play()
    transport.fill(paused)
    np.testing.assert_array_equal(paused, 0)


def test_crossfade_reads_old_audio_across_loop_boundary() -> None:
    transport = PlaybackTransport()
    old = AudioBuffer(np.array([[1], [2], [3]], dtype=np.float32), 1000)
    transport.load(old)
    transport.set_loop(True)
    transport.play()
    transport.fill(np.empty((2, 1), dtype=np.float32))
    transport.replace(AudioBuffer(np.zeros((6, 1), dtype=np.float32), 1000))
    block = np.empty((3, 1), dtype=np.float32)
    transport.fill(block)
    np.testing.assert_allclose(block[:, 0], [3, 0.5, 0])


def test_replace_rejects_channel_change_in_transport() -> None:
    transport = make_transport()
    with np.testing.assert_raises_regex(ValueError, "mesmo número de canais"):
        transport.replace(AudioBuffer(np.zeros((3, 2), dtype=np.float32), 10))
