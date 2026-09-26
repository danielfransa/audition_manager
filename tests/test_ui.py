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
        assert window.play_button.isEnabled()
        window.render()
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
