import os
from pathlib import Path
from time import monotonic, sleep

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import soundfile as sf
import pytest

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.output import OutputDevice
from audition_manager.audio.transport import PlaybackTransport, PlaybackState
from audition_manager.library.repository import ImpulseResponseRepository
from audition_manager.ui.main_window import MainWindow


class FakeOutput:
    def __init__(self) -> None:
        self.audio: AudioBuffer | None = None
        self.loop = False
        self.stopped = False
        self.transport = PlaybackTransport()
        self.loads = 0
        self.device = None
        self.gain_db = 0

    def list_devices(self) -> list[OutputDevice]:
        return [OutputDevice(3, "Test Output", "Test API")]

    def set_device(self, device: int | None) -> None:
        self.device = device

    def set_gain_db(self, gain_db: float) -> None:
        self.gain_db = gain_db

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
    window = MainWindow(output, ImpulseResponseRepository(tmp_path / "library.sqlite3"))
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
        assert window.device.count() == 2
        window.device.setCurrentIndex(1)
        assert output.device == 3
        window.gain.setValue(-12)
        assert output.gain_db == -12
        assert window.gain_label.text() == "Ganho de saída: -12 dB"
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
    window = MainWindow(output, ImpulseResponseRepository(tmp_path / "library.sqlite3"))
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
    window = MainWindow(output, ImpulseResponseRepository(tmp_path / "library.sqlite3"))
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


def test_favorite_and_rating_shortcuts_persist_after_rescan(tmp_path, monkeypatch) -> None:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    app = QApplication.instance() or QApplication([])
    database = tmp_path / "library.sqlite3"
    folder = tmp_path / "irs"
    folder.mkdir()
    ir = folder / "cab.wav"
    sf.write(ir, [1.0], 48000, subtype="FLOAT")
    monkeypatch.setattr(
        "audition_manager.ui.main_window.QFileDialog.getExistingDirectory",
        lambda *args: str(folder),
    )

    first = MainWindow(FakeOutput(), ImpulseResponseRepository(database))
    first.show()
    first.activateWindow()
    app.processEvents()
    first.choose_folder()
    first.ir_list.setCurrentRow(0)
    app.processEvents()
    QTest.keyClick(first, Qt.Key.Key_F)
    QTest.keyClick(first, Qt.Key.Key_4)
    assert first.favorite.isChecked()
    assert first.rating.text() == "Avaliação: ★★★★☆"
    first.close()

    second = MainWindow(FakeOutput(), ImpulseResponseRepository(database))
    try:
        second.choose_folder()
        second.ir_list.setCurrentRow(0)
        assert second.favorite.isChecked()
        assert second.rating.text() == "Avaliação: ★★★★☆"
    finally:
        second.close()


def test_library_filters_decorate_list_and_do_not_change_playback_selection(
    tmp_path, monkeypatch
) -> None:
    app = QApplication.instance() or QApplication([])
    folder = tmp_path / "irs"
    (folder / "Mesa").mkdir(parents=True)
    (folder / "Marshall").mkdir()
    paths = [
        folder / "Mesa" / "V30.wav",
        folder / "Marshall" / "Greenback.wav",
        folder / "Clean.wav",
    ]
    for path in paths:
        sf.write(path, [1.0], 48000, subtype="FLOAT")
    monkeypatch.setattr(
        "audition_manager.ui.main_window.QFileDialog.getExistingDirectory",
        lambda *args: str(folder),
    )
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    window = MainWindow(FakeOutput(), repository)
    try:
        window.choose_folder()
        assert window.ir_list.count() == 3
        mesa_row = window.ir_paths.index(paths[0].resolve())
        window.ir_list.setCurrentRow(mesa_row)
        repository.set_favorite(paths[0], True)
        repository.set_rating(paths[0], 5)
        repository.set_rating(paths[1], 3)
        version = window.selection_version
        window.apply_filters()
        assert window.selection_version == version
        assert "★ " in window.ir_list.currentItem().text()
        assert "★★★★★" in window.ir_list.currentItem().text()

        window.search.setText("green")
        assert window.ir_list.count() == 1
        assert "Greenback.wav" in window.ir_list.item(0).text()
        window.search.clear()
        window.favorites_only.setChecked(True)
        assert window.ir_list.count() == 1
        assert "V30.wav" in window.ir_list.item(0).text()
        window.favorites_only.setChecked(False)
        window.minimum_rating.setCurrentIndex(4)
        assert window.ir_list.count() == 1
        assert "V30.wav" in window.ir_list.item(0).text()
        assert window.selection_version == version
    finally:
        window.close()


def test_notes_persist_and_typing_does_not_trigger_global_shortcuts(
    tmp_path, monkeypatch
) -> None:
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest

    app = QApplication.instance() or QApplication([])
    folder = tmp_path / "irs"
    folder.mkdir()
    ir = folder / "cab.wav"
    sf.write(ir, [1.0], 48000, subtype="FLOAT")
    monkeypatch.setattr(
        "audition_manager.ui.main_window.QFileDialog.getExistingDirectory",
        lambda *args: str(folder),
    )
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    window = MainWindow(FakeOutput(), repository)
    try:
        window.show()
        window.activateWindow()
        window.choose_folder()
        window.ir_list.setCurrentRow(0)
        app.processEvents()
        window.notes.setFocus()
        QTest.keyClicks(window.notes, "F B 12345 favorite test")
        QTest.keyClick(window.notes, Qt.Key.Key_Space)
        assert not window.favorite.isChecked()
        assert not window.bypass.isChecked()
        assert repository.get(ir).rating == 0
        window.save_notes_button.click()
        assert repository.get(ir).notes == "F B 12345 favorite test "
        window.notes.clear()
        window.refresh_metadata()
        assert window.notes.toPlainText() == "F B 12345 favorite test "
        assert window.status.text() == "Notas salvas."
    finally:
        window.close()
