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
