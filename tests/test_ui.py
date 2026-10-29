import os
from pathlib import Path
from time import monotonic, sleep

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import soundfile as sf
import pytest
import json
import numpy as np

qt_widgets = pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)
QApplication = qt_widgets.QApplication

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.output import OutputDevice
from audition_manager.audio.transport import PlaybackTransport, PlaybackState
from audition_manager.config.preferences import PreferencesStore, UserPreferences
from audition_manager.library.repository import ImpulseResponseRepository
from audition_manager.library.models import ImpulseResponse
from audition_manager.ui.main_window import (
    ExportOptionsDialog, MainWindow, create_ir_directory_dialog,
)


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


class FakeNamRenderer:
    def __init__(self) -> None:
        self.models: list[Path] = []
        self.qualities: list[str] = []

    def render(
        self, source: AudioBuffer, model_path: Path, quality: str = "full"
    ) -> AudioBuffer:
        self.models.append(model_path)
        self.qualities.append(quality)
        mono = np.mean(source.samples, axis=1, keepdims=True, dtype=np.float32)
        return AudioBuffer(mono * 2, source.sample_rate)


def wait_for_scan(window: MainWindow, app: QApplication, timeout: float = 5) -> None:
    deadline = monotonic() + timeout
    while window.scan_worker is not None and monotonic() < deadline:
        app.processEvents()
        sleep(0.01)
    assert window.scan_worker is None


def test_ir_directory_dialog_shows_wav_files_and_selects_directory() -> None:
    app = QApplication.instance() or QApplication([])
    dialog = create_ir_directory_dialog(None, "")
    try:
        assert dialog.fileMode() == dialog.FileMode.Directory
        assert not dialog.testOption(dialog.Option.ShowDirsOnly)
        assert dialog.testOption(dialog.Option.DontUseNativeDialog)
        assert dialog.nameFilters() == ["Impulse Responses WAV (*.wav *.WAV)"]
        assert (
            dialog.labelText(dialog.DialogLabel.Accept) == "Escolher esta pasta"
        )
    finally:
        dialog.close()


def test_export_options_default_to_both_and_require_one_category() -> None:
    app = QApplication.instance() or QApplication([])
    dialog = ExportOptionsDialog()
    try:
        ok = dialog.buttons.button(dialog.buttons.StandardButton.Ok)
        assert dialog.folder_name.text() == "Audition Manager Favorites"
        assert dialog.export_captures.isChecked()
        assert dialog.export_irs.isChecked()
        assert ok.isEnabled()
        dialog.export_captures.setChecked(False)
        dialog.export_irs.setChecked(False)
        assert not ok.isEnabled()
        dialog.export_irs.setChecked(True)
        assert ok.isEnabled()
    finally:
        dialog.close()


def test_language_switch_updates_interface_and_persists(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    store = PreferencesStore(tmp_path / "preferences.json")
    window = MainWindow(
        FakeOutput(), ImpulseResponseRepository(tmp_path / "library.sqlite3"), store
    )
    try:
        window.language.setCurrentIndex(window.language.findData("en"))
        assert window.di_button.text() == "Open DI WAV"
        assert window.folder_button.text() == "Select IR folder"
        assert window.capture_button.text() == "Select NAM capture folder"
        assert window.export_button.text() == "Export favorites…"
        assert window.play_button.text() == "Process and play"
        assert window.language_label.text() == "Language:"
        assert store.load().language == "en"
        window.language.setCurrentIndex(window.language.findData("pt_BR"))
        assert window.di_button.text() == "Abrir DI WAV"
        assert store.load().language == "pt_BR"
    finally:
        window.close()


def test_audio_lists_keep_a_practical_minimum_height(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = MainWindow(
        FakeOutput(),
        ImpulseResponseRepository(tmp_path / "library.sqlite3"),
        PreferencesStore(tmp_path / "preferences.json"),
    )
    try:
        assert window.capture_list.minimumHeight() >= 110
        assert window.ir_list.minimumHeight() >= 110
        assert window.size().width() >= 960
        assert window.size().height() >= 900
        assert window.content_scroll.widgetResizable()
        assert window.content_scroll.widget() is not None
        window.resize(760, 700)
        window.show()
        app.processEvents()
        assert window.content_scroll.verticalScrollBar().maximum() > 0
    finally:
        window.close()


def test_restores_and_updates_application_preferences(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    di = tmp_path / "di.wav"
    ir_folder = tmp_path / "irs"
    capture_folder = tmp_path / "captures"
    export_folder = tmp_path / "exports"
    ir_folder.mkdir()
    capture_folder.mkdir()
    export_folder.mkdir()
    sf.write(di, [0.1], 48000)
    sf.write(ir_folder / "cab.wav", [1.0], 48000, subtype="FLOAT")
    capture = capture_folder / "amp.nam"
    capture.write_text(json.dumps({
        "version": "0.7.0", "architecture": "SlimmableContainer",
        "sample_rate": 48000,
        "config": {"submodels": [{"model": {"architecture": "WaveNet"}}]},
    }), encoding="utf-8")
    store = PreferencesStore(tmp_path / "preferences.json")
    store.save(
        UserPreferences(
            last_di_file=di,
            last_ir_directory=ir_folder,
            last_capture_directory=capture_folder,
            last_capture_file=capture,
            last_export_directory=export_folder,
            output_device_name="Test Output",
            output_host_api="Test API",
            output_gain_db=-9,
            loop_enabled=False,
        )
    )
    output = FakeOutput()
    window = MainWindow(
        output, ImpulseResponseRepository(tmp_path / "library.sqlite3"), store
    )
    try:
        wait_for_scan(window, app)
        assert window.di_path == di.resolve()
        assert window.ir_root == ir_folder.resolve()
        assert window.ir_list.count() == 1
        assert window.capture_list.count() == 1
        assert window.selected_capture_path() == capture.resolve()
        assert window.device.currentIndex() == 1
        assert output.device == 3
        assert window.gain.value() == -9
        assert output.gain_db == -9
        assert not window.loop.isChecked()
        assert not output.loop
        window.gain.setValue(-15)
        window.loop.setChecked(True)
        window.device.setCurrentIndex(0)
    finally:
        window.close()
    saved = store.load()
    assert saved.output_gain_db == -15
    assert saved.loop_enabled
    assert saved.output_device_name is None
    assert saved.last_export_directory == export_folder


def test_missing_saved_resources_fall_back_without_blocking_startup(
    tmp_path: Path,
) -> None:
    app = QApplication.instance() or QApplication([])
    store = PreferencesStore(tmp_path / "preferences.json")
    store.save(
        UserPreferences(
            last_di_file=tmp_path / "missing.wav",
            last_ir_directory=tmp_path / "missing-irs",
            last_export_directory=tmp_path / "missing-exports",
            output_device_name="Disconnected",
            output_host_api="Test API",
        )
    )
    output = FakeOutput()
    window = MainWindow(
        output, ImpulseResponseRepository(tmp_path / "library.sqlite3"), store
    )
    try:
        app.processEvents()
        assert window.di_path is None
        assert window.scan_worker is None
        assert window.device.currentIndex() == 0
        assert output.device is None
        assert store.load() == UserPreferences()
    finally:
        window.close()


def test_select_render_play_and_stop(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    output = FakeOutput()
    window = MainWindow(
        output,
        ImpulseResponseRepository(tmp_path / "library.sqlite3"),
        PreferencesStore(tmp_path / "preferences.json"),
    )
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
        "audition_manager.ui.main_window.choose_ir_directory",
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
        wait_for_scan(window, app)
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


def test_capture_and_ir_are_processed_as_one_chain(tmp_path: Path, monkeypatch) -> None:
    app = QApplication.instance() or QApplication([])
    output = FakeOutput()
    renderer = FakeNamRenderer()
    window = MainWindow(
        output,
        ImpulseResponseRepository(tmp_path / "library.sqlite3"),
        PreferencesStore(tmp_path / "preferences.json"),
        renderer,
    )
    di = tmp_path / "di.wav"
    ir_folder = tmp_path / "irs"
    capture_folder = tmp_path / "captures"
    ir_folder.mkdir()
    capture_folder.mkdir()
    sf.write(di, [0.1, 0.2], 48000, subtype="FLOAT")
    sf.write(ir_folder / "cab.wav", [1.0], 48000, subtype="FLOAT")
    model = capture_folder / "amp.nam"
    model.write_text(json.dumps({
        "version": "0.7.0", "architecture": "SlimmableContainer",
        "sample_rate": 48000,
        "config": {"submodels": [{"model": {"architecture": "WaveNet"}}]},
    }), encoding="utf-8")
    monkeypatch.setattr(
        "audition_manager.ui.main_window.choose_ir_directory",
        lambda *args: str(ir_folder),
    )
    monkeypatch.setattr(
        "audition_manager.ui.main_window.choose_nam_directory",
        lambda *args: str(capture_folder),
    )
    try:
        window.di_path = di
        window.choose_folder()
        wait_for_scan(window, app)
        window.choose_capture_folder()
        assert window.capture_list.count() == 1
        window.capture_list.setCurrentRow(0)
        window.capture_rating.buttons[3].click()
        window.capture_favorite.setChecked(True)
        window.capture_notes.setPlainText("My amp notes")
        window.save_capture_notes_button.click()
        capture_item = window.repository.get_capture(model)
        assert capture_item is not None
        assert (capture_item.rating, capture_item.favorite, capture_item.notes) == (
            4, True, "My amp notes"
        )
        window.ir_list.setCurrentRow(0)
        deadline = monotonic() + 5
        while window.worker is not None and monotonic() < deadline:
            app.processEvents()
            sleep(0.01)
        assert renderer.models == [model.resolve()]
        assert output.audio is not None
        assert output.audio.samples[:, 0] == pytest.approx([0.2, 0.4])
        assert "NAM A2 Full (amp.nam) → IR (cab.wav)" in window.active_ir.text()
        assert window.peak_meter.format().startswith("Pico: ")
        window.nam_quality.setCurrentIndex(window.nam_quality.findData("lite"))
        deadline = monotonic() + 5
        while window.worker is not None and monotonic() < deadline:
            app.processEvents()
            sleep(0.01)
        assert renderer.qualities == ["full", "lite"]
        assert "NAM A2 Lite" in window.active_ir.text()
        window.capture_gain.setValue(6)
        deadline = monotonic() + 5
        while window.worker is not None and monotonic() < deadline:
            app.processEvents()
            sleep(0.01)
        assert output.audio.samples[:, 0] == pytest.approx(
            [0.2 * (10 ** (6 / 20)), 0.4 * (10 ** (6 / 20))]
        )
        window.capture_bypass.setChecked(True)
        deadline = monotonic() + 5
        while window.worker is not None and monotonic() < deadline:
            app.processEvents()
            sleep(0.01)
        assert renderer.models == [model.resolve(), model.resolve(), model.resolve()]
        assert output.audio.samples[:, 0] == pytest.approx([0.1, 0.2])
        assert window.active_ir.text() == (
            "Cadeia ativa: DI → IR (cab.wav) — Bypass ativo: NAM"
        )
        window.capture_search.setText("missing")
        assert window.capture_list.count() == 0
        window.capture_search.clear()
        assert window.capture_list.count() == 1
        window.capture_favorites_only.setChecked(True)
        assert window.capture_list.count() == 1
    finally:
        if window.worker is not None:
            window.worker.wait()
            app.processEvents()
        window.close()


def test_legacy_nam_is_listed_and_disables_a2_quality_selector(
    tmp_path: Path, monkeypatch
) -> None:
    app = QApplication.instance() or QApplication([])
    folder = tmp_path / "captures"
    folder.mkdir()
    model = folder / "legacy.nam"
    model.write_text(json.dumps({
        "version": "0.5.4", "architecture": "WaveNet",
        "sample_rate": 48000, "config": {}, "weights": [],
    }), encoding="utf-8")
    monkeypatch.setattr(
        "audition_manager.ui.main_window.choose_nam_directory",
        lambda *args: str(folder),
    )
    window = MainWindow(
        FakeOutput(), ImpulseResponseRepository(tmp_path / "library.sqlite3"),
        PreferencesStore(tmp_path / "preferences.json"), FakeNamRenderer(),
    )
    try:
        window.choose_capture_folder()
        assert window.capture_list.count() == 1
        assert "WaveNet v0.5.4" in window.capture_list.item(0).text()
        window.capture_list.setCurrentRow(0)
        assert not window.nam_quality.isEnabled()
    finally:
        window.close()


@pytest.mark.parametrize("use_bypass", [False, True])
def test_latest_selection_wins_and_stop_during_render_does_not_autoplay(monkeypatch, tmp_path, use_bypass) -> None:
    from threading import Event
    import numpy as np

    app = QApplication.instance() or QApplication([])
    output = FakeOutput()
    window = MainWindow(
        output,
        ImpulseResponseRepository(tmp_path / "library.sqlite3"),
        PreferencesStore(tmp_path / "preferences.json"),
    )
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
    window = MainWindow(
        output,
        ImpulseResponseRepository(tmp_path / "library.sqlite3"),
        PreferencesStore(tmp_path / "preferences.json"),
    )
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
        "audition_manager.ui.main_window.choose_ir_directory",
        lambda *args: str(folder),
    )

    preferences = PreferencesStore(tmp_path / "preferences.json")
    first = MainWindow(FakeOutput(), ImpulseResponseRepository(database), preferences)
    first.show()
    first.activateWindow()
    app.processEvents()
    first.choose_folder()
    wait_for_scan(first, app)
    first.ir_list.setCurrentRow(0)
    app.processEvents()
    QTest.keyClick(first, Qt.Key.Key_F)
    QTest.keyClick(first, Qt.Key.Key_4)
    assert first.favorite.isChecked()
    assert first.rating.text() == "Avaliação: ★★★★☆"
    QTest.mouseClick(first.rating.buttons[1], Qt.MouseButton.LeftButton)
    assert first.rating.text() == "Avaliação: ★★☆☆☆"
    assert first.repository.get(ir).rating == 2
    QTest.mouseClick(first.rating.buttons[3], Qt.MouseButton.LeftButton)
    assert first.rating.text() == "Avaliação: ★★★★☆"
    first.close()

    second = MainWindow(FakeOutput(), ImpulseResponseRepository(database), preferences)
    try:
        wait_for_scan(second, app)
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
        "audition_manager.ui.main_window.choose_ir_directory",
        lambda *args: str(folder),
    )
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    window = MainWindow(
        FakeOutput(), repository, PreferencesStore(tmp_path / "preferences.json")
    )
    try:
        window.choose_folder()
        wait_for_scan(window, app)
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
        "audition_manager.ui.main_window.choose_ir_directory",
        lambda *args: str(folder),
    )
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    window = MainWindow(
        FakeOutput(), repository, PreferencesStore(tmp_path / "preferences.json")
    )
    try:
        window.show()
        window.activateWindow()
        window.choose_folder()
        wait_for_scan(window, app)
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


def test_exports_all_favorites_from_current_root_regardless_of_filters(
    tmp_path, monkeypatch
) -> None:
    app = QApplication.instance() or QApplication([])
    source = tmp_path / "irs"
    capture_source = tmp_path / "captures"
    nested = source / "Mesa"
    nested.mkdir(parents=True)
    favorites = [nested / "V30.wav", source / "Clean.wav"]
    other = source / "Other.wav"
    for path in [*favorites, other]:
        sf.write(path, [1.0], 48000, subtype="FLOAT")
    capture_source.mkdir()
    capture = capture_source / "Favorite Amp.nam"
    capture.write_text(json.dumps({
        "version": "0.7.0", "architecture": "SlimmableContainer",
        "sample_rate": 48000,
        "config": {"submodels": [{"model": {"architecture": "WaveNet"}}]},
    }), encoding="utf-8")
    destination = tmp_path / "exports"
    destination.mkdir()
    monkeypatch.setattr(
        "audition_manager.ui.main_window.choose_ir_directory",
        lambda *args: str(source),
    )
    monkeypatch.setattr(
        "audition_manager.ui.main_window.choose_nam_directory",
        lambda *args: str(capture_source),
    )
    monkeypatch.setattr(
        "audition_manager.ui.main_window.QFileDialog.getExistingDirectory",
        lambda *args: str(destination),
    )
    monkeypatch.setattr(
        "audition_manager.ui.main_window.choose_export_options",
        lambda *args: ("My Pedal IRs", False, True, True),
    )
    messages = []
    monkeypatch.setattr(
        "audition_manager.ui.main_window.QMessageBox.information",
        lambda *args: messages.append(args[-1]),
    )
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    window = MainWindow(
        FakeOutput(), repository, PreferencesStore(tmp_path / "preferences.json")
    )
    try:
        window.choose_folder()
        wait_for_scan(window, app)
        window.choose_capture_folder()
        for path in favorites:
            repository.set_favorite(path, True)
        repository.set_capture_favorite(capture, True)
        window.apply_filters()
        window.apply_capture_filters()
        assert window.export_button.isEnabled()
        window.search.setText("V30")
        assert window.ir_list.count() == 1
        window.export_button.click()
        exported = destination / "My Pedal IRs"
        assert (exported / "IRs" / "Mesa" / "V30.wav").exists()
        assert (exported / "IRs" / "Clean.wav").exists()
        assert not (exported / "IRs" / "Other.wav").exists()
        assert not (exported / "Capturas").exists()
        assert "2 favoritos exportados (0 capturas, 2 IRs)" in window.status.text()
        assert messages == [window.status.text()]
    finally:
        window.close()


def test_newest_async_scan_wins_and_old_library_remains_visible(
    tmp_path, monkeypatch
) -> None:
    from threading import Event

    app = QApplication.instance() or QApplication([])
    original = tmp_path / "original"
    first = tmp_path / "first"
    latest = tmp_path / "latest"
    for root in (original, first, latest):
        root.mkdir()
        (root / f"{root.name}.wav").touch()
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    repository.upsert_many([
        ImpulseResponse((original / "original.wav").resolve(), "original.wav", 48000, 1)
    ])
    window = MainWindow(
        FakeOutput(), repository, PreferencesStore(tmp_path / "preferences.json")
    )
    window.ir_root = original.resolve()
    window.all_ir_paths = [(original / "original.wav").resolve()]
    window.apply_filters()
    entered = Event()
    release = Event()

    monkeypatch.setattr(
        "audition_manager.ui.main_window.scan_wavs",
        lambda root: [root / f"{root.name}.wav"],
    )

    def inspect(path):
        if path.parent == first.resolve():
            entered.set()
            assert release.wait(5)
        return ImpulseResponse(path.resolve(), path.name, 44100, 1)

    monkeypatch.setattr("audition_manager.ui.main_window.inspect_wav", inspect)
    try:
        window.begin_scan(first)
        assert entered.wait(2)
        assert window.ir_list.item(0).text().startswith("original.wav")
        assert not window.scan_progress.isHidden()
        window.begin_scan(latest)
        release.set()
        wait_for_scan(window, app)
        assert window.ir_root == latest.resolve()
        assert window.all_ir_paths == [(latest / "latest.wav").resolve()]
        assert window.ir_list.item(0).text().startswith("latest.wav")
        assert window.scan_progress.isHidden()
    finally:
        release.set()
        if window.scan_worker is not None:
            window.scan_worker.requestInterruption()
            window.scan_worker.wait()
            app.processEvents()
        window.close()


def test_cancel_scan_keeps_previous_library(tmp_path, monkeypatch) -> None:
    from threading import Event

    app = QApplication.instance() or QApplication([])
    original = tmp_path / "original"
    pending = tmp_path / "pending"
    original.mkdir()
    pending.mkdir()
    old_path = original / "old.wav"
    new_path = pending / "new.wav"
    old_path.touch()
    new_path.touch()
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    repository.upsert_many([ImpulseResponse(old_path.resolve(), old_path.name, 48000, 1)])
    window = MainWindow(
        FakeOutput(), repository, PreferencesStore(tmp_path / "preferences.json")
    )
    window.ir_root = original.resolve()
    window.all_ir_paths = [old_path.resolve()]
    window.apply_filters()
    entered = Event()
    release = Event()
    monkeypatch.setattr(
        "audition_manager.ui.main_window.scan_wavs", lambda root: [new_path]
    )

    def inspect(path):
        entered.set()
        assert release.wait(5)
        return ImpulseResponse(path.resolve(), path.name, 48000, 1)

    monkeypatch.setattr("audition_manager.ui.main_window.inspect_wav", inspect)
    try:
        window.begin_scan(pending)
        assert entered.wait(2)
        window.cancel_scan()
        release.set()
        wait_for_scan(window, app)
        assert window.ir_root == original.resolve()
        assert window.all_ir_paths == [old_path.resolve()]
        assert window.ir_list.item(0).text().startswith("old.wav")
        assert "cancelado" in window.status.text().casefold()
    finally:
        release.set()
        if window.scan_worker is not None:
            window.scan_worker.requestInterruption()
            window.scan_worker.wait()
            app.processEvents()
        window.close()
