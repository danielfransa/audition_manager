import os
from pathlib import Path
from time import monotonic, sleep

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import soundfile as sf
import pytest

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.transport import PlaybackTransport, PlaybackState
from audition_manager.ui.main_window import MainWindow


class FakeOutput:
    def __init__(self) -> None:
        self.audio: AudioBuffer | None = None
        self.loop = False
        self.stopped = False
        self.transport = PlaybackTransport()
        self.loads = 0

    def play(self, audio: AudioBuffer | None = None, *, loop: bool = False) -> None:
        if audio is not None:
            self.audio = audio
            self.transport.load(audio)
            self.loads += 1
        self.loop = loop
        self.transport.set_loop(loop)
        self.transport.play()

    def load(self, audio: AudioBuffer) -> None:
        self.audio = audio
        self.transport.load(audio)
        self.loads += 1

    def replace(self, audio: AudioBuffer) -> None:
        self.audio = audio
        self.transport.replace(audio)
        self.loads += 1

    def pause(self) -> None:
        self.transport.pause()

    def set_loop(self, enabled: bool) -> None:
        self.loop = enabled
        self.transport.set_loop(enabled)

    def close(self) -> None:
        self.transport.clear()

    def stop(self) -> None:
        self.stopped = True
        self.transport.stop()


def test_select_render_play_and_stop(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    output = FakeOutput()
    window = MainWindow(output)
    di = tmp_path / "di.wav"
    ir_folder = tmp_path / "irs"
    ir_folder.mkdir()
    sf.write(di, [0.1, 0.2], 48000)
    sf.write(ir_folder / "cab.wav", [1.0], 48000, subtype="FLOAT")
    monkeypatch.setattr(
        "audition_manager.ui.main_window.QFileDialog.getOpenFileName",
        lambda *args: (str(di), ""),
    )
    monkeypatch.setattr(
        "audition_manager.ui.main_window.QFileDialog.getExistingDirectory",
        lambda *args: str(ir_folder),
    )
    try:
        assert not window.play_button.isEnabled()
        window.choose_di()
        window.choose_folder()
        assert window.ir_list.count() == 1
        window.ir_list.setCurrentRow(0)
        assert not window.play_button.isEnabled()
        deadline = monotonic() + 10
        while window.worker is not None and monotonic() < deadline:
            app.processEvents()
            sleep(0.01)
        assert window.worker is None
        assert output.audio is not None
        assert output.audio.sample_rate == 48000
        assert output.loop
        assert window.play_button.isEnabled()
        window.render()
        assert output.transport.snapshot()[0] == PlaybackState.PAUSED
        window.render()
        assert output.transport.snapshot()[0] == PlaybackState.PLAYING
        assert output.loads == 1
        window.loop.setChecked(False)
        assert not output.loop
        window.stop()
        assert output.stopped
        window.render()
        assert output.loads == 1
        window.choose_di()
        assert not window.has_rendered_audio
        assert output.transport.snapshot()[0] == PlaybackState.EMPTY
    finally:
        if window.worker is not None:
            window.worker.wait()
            app.processEvents()
        window.close()


@pytest.mark.parametrize("use_bypass", [False, True])
def test_latest_selection_wins_and_stop_during_render_does_not_autoplay(monkeypatch, tmp_path, use_bypass) -> None:
    from threading import Event
    import numpy as np

    app = QApplication.instance() or QApplication([])
    output = FakeOutput()
    window = MainWindow(output)
    entered, release = Event(), Event()
    calls = []

    def render(di, ir):
        calls.append(ir.name)
        if len(calls) == 1:
            entered.set()
            assert release.wait(5)
        return AudioBuffer(np.full((10, 1), 0.3, dtype=np.float32), 48000)

    monkeypatch.setattr("audition_manager.ui.main_window.render_files", render)
    window.di_path = tmp_path / "di.wav"
    sf.write(window.di_path, [0.1, 0.2], 48000, subtype="FLOAT")
    window.ir_paths = [tmp_path / name for name in ("first.wav", "middle.wav", "last.wav")]
    for path in window.ir_paths:
        path.touch()
    window.ir_list.addItems([path.name for path in window.ir_paths])
    try:
        window.ir_list.setCurrentRow(0)
        assert entered.wait(2)
        window.move_ir(1)
        window.move_ir(1)
        if use_bypass:
            window.bypass.setChecked(True)
        window.stop()
        release.set()
        deadline = monotonic() + 5
        while window.worker is not None and monotonic() < deadline:
            app.processEvents()
            sleep(0.01)
        assert window.worker is None
        assert calls == (["first.wav"] if use_bypass else ["first.wav", "last.wav"])
        assert output.loads == 1
        assert output.transport.snapshot()[0] == PlaybackState.STOPPED
        assert ("Bypass ativo" if use_bypass else "last.wav") in window.active_ir.text()
    finally:
        release.set()
        if window.worker is not None:
            window.worker.wait()
            app.processEvents()
        window.close()


def test_bypass_preserves_pause_and_shortcuts_control_player(tmp_path, monkeypatch) -> None:
    import numpy as np
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from audition_manager.audio.ir_processor import render_files

    app = QApplication.instance() or QApplication([])
    output = FakeOutput()
    window = MainWindow(output)
    di, ir = tmp_path / "di.wav", tmp_path / "ir.wav"
    sf.write(di, np.full(4800, 0.1), 48000, subtype="FLOAT")
    sf.write(ir, [0.5], 48000, subtype="FLOAT")
    calls = []

    def tracked_render(di_path, ir_path):
        calls.append(ir_path)
        return render_files(di_path, ir_path)

    monkeypatch.setattr("audition_manager.ui.main_window.render_files", tracked_render)
    window.di_path = di
    window.ir_paths = [ir]
    window.ir_list.addItem(ir.name)

    def wait_render():
        deadline = monotonic() + 5
        while window.worker is not None and monotonic() < deadline:
            app.processEvents()
            sleep(0.01)
        assert window.worker is None

    try:
        window.show()
        window.activateWindow()
        app.processEvents()
        window.ir_list.setCurrentRow(0)
        wait_render()
        output.transport.fill(np.zeros((100, 1), dtype=np.float32))
        QTest.keyClick(window, Qt.Key.Key_Space)
        assert output.transport.snapshot()[0] == PlaybackState.PAUSED
        position = output.transport.snapshot()[1]
        QTest.keyClick(window, Qt.Key.Key_B)
        wait_render()
        assert window.bypass.isChecked()
        assert output.transport.snapshot()[0] == PlaybackState.PAUSED
        assert output.transport.snapshot()[1] == position
        np.testing.assert_allclose(output.audio.samples, 0.1)
        assert "Bypass ativo" in window.active_ir.text()
        QTest.keyClick(window, Qt.Key.Key_B)
        wait_render()
        np.testing.assert_allclose(output.audio.samples, 0.05, atol=1e-7)
        assert len(calls) == 1
        QTest.keyClick(window, Qt.Key.Key_Space)
        assert output.transport.snapshot()[0] == PlaybackState.PLAYING
    finally:
        if window.worker is not None:
            window.worker.wait()
            app.processEvents()
        window.close()
