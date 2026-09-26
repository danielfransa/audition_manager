import logging
from pathlib import Path

from PySide6.QtCore import QThread, QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.ir_processor import render_files
from audition_manager.audio.output import AudioOutput
from audition_manager.audio.transport import PlaybackState
from audition_manager.library.scanner import scan_wavs

logger = logging.getLogger(__name__)


def format_time(seconds: float) -> str:
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remainder:02d}"


class RenderWorker(QThread):
    rendered = Signal(object)
    failed = Signal(str)

    def __init__(self, di_path: Path, ir_path: Path, parent: QWidget) -> None:
        super().__init__(parent)
        self.di_path = di_path
        self.ir_path = ir_path

    def run(self) -> None:
        try:
            self.rendered.emit(render_files(self.di_path, self.ir_path))
        except Exception as error:
            logger.exception("Unable to render audio")
            self.failed.emit(str(error))


class MainWindow(QMainWindow):
    def __init__(self, output: AudioOutput) -> None:
        super().__init__()
        self.output = output
        self.di_path: Path | None = None
        self.ir_paths: list[Path] = []
        self.worker: RenderWorker | None = None
        self.has_rendered_audio = False
        self.setWindowTitle("Audition Manager")
        self.resize(720, 520)
        self.di_label = QLabel("Nenhuma DI selecionada")
        self.di_button = QPushButton("Abrir DI WAV")
        self.folder_button = QPushButton("Selecionar pasta de IRs")
        self.ir_list = QListWidget()
        self.loop = QCheckBox("Loop")
        self.loop.setChecked(True)
        self.play_button = QPushButton("Processar e reproduzir")
        self.play_button.setEnabled(False)
        self.stop_button = QPushButton("Stop")
        self.position_label = QLabel("00:00 / 00:00")
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setTextVisible(False)
        self.status = QLabel("Abra uma DI e selecione um IR.")
        self.status.setWordWrap(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        for widget in (
            self.di_label, self.di_button, self.folder_button, self.ir_list,
            self.loop, self.play_button, self.stop_button,
            self.position_label, self.progress, self.status,
        ):
            layout.addWidget(widget)
        self.setCentralWidget(container)
        self.di_button.clicked.connect(self.choose_di)
        self.folder_button.clicked.connect(self.choose_folder)
        self.ir_list.currentRowChanged.connect(self.selection_changed)
        self.play_button.clicked.connect(self.render)
        self.stop_button.clicked.connect(self.stop)
        self.loop.toggled.connect(self.output.set_loop)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.refresh_playback)
        self.timer.start()

    @Slot()
    def choose_di(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir DI", "", "WAV (*.wav *.WAV)")
        if filename:
            self.di_path = Path(filename)
            self.di_label.setText(f"DI: {self.di_path.name}")
            self.selection_changed()

    @Slot()
    def choose_folder(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Pasta de IRs")
        if not directory:
            return
        try:
            root = Path(directory)
            paths = scan_wavs(root)
        except (OSError, ValueError) as error:
            self.show_error(str(error))
            return
        self.ir_list.clear()
        self.ir_paths = paths
        self.ir_list.addItems([str(path.relative_to(root)) for path in paths])
        self.status.setText(f"{len(paths)} arquivos WAV encontrados; selecione um IR.")

    @Slot()
    def selection_changed(self) -> None:
        try:
            self.output.close()
        except Exception as error:
            logger.exception("Unable to release audio output")
            self.show_error(str(error))
        self.has_rendered_audio = False
        self.refresh_playback()
        self.update_play_button()

    @Slot()
    def refresh_playback(self) -> None:
        state, position, duration = self.output.transport.snapshot()
        labels = {
            PlaybackState.EMPTY: "Sem áudio", PlaybackState.STOPPED: "Parado",
            PlaybackState.PLAYING: "Reproduzindo", PlaybackState.PAUSED: "Pausado",
            PlaybackState.FINISHED: "Finalizado",
        }
        self.position_label.setText(
            f"{format_time(position)} / {format_time(duration)} — {labels[state]}"
        )
        self.progress.setValue(round(1000 * position / duration) if duration else 0)
        if self.worker is None:
            self.play_button.setText(
                "Pause" if state == PlaybackState.PLAYING else
                "Play" if self.has_rendered_audio else "Processar e reproduzir"
            )

    @Slot()
    def update_play_button(self) -> None:
        self.play_button.setEnabled(
            self.worker is None and self.di_path is not None and self.ir_list.currentRow() >= 0
        )

    @Slot()
    def render(self) -> None:
        row = self.ir_list.currentRow()
        if self.worker is not None or self.di_path is None or row < 0:
            return
        if self.has_rendered_audio:
            try:
                state, _, _ = self.output.transport.snapshot()
                if state == PlaybackState.PLAYING:
                    self.output.pause()
                else:
                    self.output.play(loop=self.loop.isChecked())
                self.status.setText("Player pronto.")
                self.refresh_playback()
            except Exception as error:
                logger.exception("Unable to control playback")
                self.show_error(str(error))
            return
        self.worker = RenderWorker(self.di_path, self.ir_paths[row], self)
        self.worker.rendered.connect(self.play_rendered)
        self.worker.failed.connect(self.show_error)
        self.worker.finished.connect(self.render_finished)
        self.set_busy(True)
        self.status.setText("Processando DI + IR…")
        self.worker.start()

    @Slot(object)
    def play_rendered(self, audio: AudioBuffer) -> None:
        try:
            self.output.play(audio, loop=self.loop.isChecked())
        except Exception as error:
            logger.exception("Unable to open audio output")
            self.show_error(str(error))
            return
        self.has_rendered_audio = True
        self.status.setText("Pause mantém a posição; Stop volta ao início.")

    @Slot()
    def render_finished(self) -> None:
        if self.worker is not None:
            self.worker.deleteLater()
        self.worker = None
        self.set_busy(False)
        self.refresh_playback()

    def set_busy(self, busy: bool) -> None:
        for widget in (self.di_button, self.folder_button, self.ir_list, self.loop, self.stop_button):
            widget.setEnabled(not busy)
        self.update_play_button()

    @Slot()
    def stop(self) -> None:
        try:
            self.output.stop()
            self.status.setText("Reprodução parada.")
            self.refresh_playback()
        except Exception as error:
            logger.exception("Unable to stop audio output")
            self.show_error(str(error))

    @Slot(str)
    def show_error(self, message: str) -> None:
        self.status.setText("Não foi possível concluir a operação.")
        QMessageBox.warning(self, "Audition Manager", message)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.worker is not None:
            self.status.setText("Aguarde o processamento terminar antes de fechar.")
            event.ignore()
            return
        try:
            self.output.close()
        except Exception as error:
            logger.exception("Unable to close audio output")
            self.show_error(str(error))
            event.ignore()
            return
        self.timer.stop()
        event.accept()
