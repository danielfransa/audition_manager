import logging
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
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
from audition_manager.audio.render_cache import RenderCache
from audition_manager.audio.transport import PlaybackState
from audition_manager.library.scanner import scan_wavs
from audition_manager.library.repository import ImpulseResponseRepository
from audition_manager.library.scanner import inspect_wavs

logger = logging.getLogger(__name__)


def format_time(seconds: float) -> str:
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remainder:02d}"


class RenderWorker(QThread):
    rendered = Signal(object)
    failed = Signal(str)

    def __init__(
        self, di_path: Path, ir_path: Path | None, cache: RenderCache, parent: QWidget
    ) -> None:
        super().__init__(parent)
        self.di_path = di_path
        self.ir_path = ir_path
        self.cache = cache

    def run(self) -> None:
        try:
            self.rendered.emit(self.cache.render(self.di_path, self.ir_path, render_files))
        except Exception as error:
            logger.exception("Unable to render audio")
            self.failed.emit(str(error))


class MainWindow(QMainWindow):
    def __init__(
        self, output: AudioOutput, repository: ImpulseResponseRepository
    ) -> None:
        super().__init__()
        self.output = output
        self.repository = repository
        self.di_path: Path | None = None
        self.ir_paths: list[Path] = []
        self.worker: RenderWorker | None = None
        self.cache = RenderCache()
        self.has_rendered_audio = False
        self.selection_version = 0
        self.worker_version = -1
        self.autoplay = True
        self.setWindowTitle("Audition Manager")
        self.resize(720, 520)
        self.di_label = QLabel("Nenhuma DI selecionada")
        self.di_button = QPushButton("Abrir DI WAV")
        self.folder_button = QPushButton("Selecionar pasta de IRs")
        self.ir_list = QListWidget()
        self.bypass = QCheckBox("Bypass IR (B)")
        self.loop = QCheckBox("Loop")
        self.loop.setChecked(True)
        self.play_button = QPushButton("Processar e reproduzir")
        self.play_button.setEnabled(False)
        self.stop_button = QPushButton("Stop")
        self.position_label = QLabel("00:00 / 00:00")
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setTextVisible(False)
        self.active_ir = QLabel("IR em reprodução: nenhum")
        self.favorite = QCheckBox("Favorito (F)")
        self.favorite.setEnabled(False)
        self.rating = QLabel("Avaliação: ☆☆☆☆☆")
        self.status = QLabel("Abra uma DI e selecione um IR.")
        self.status.setWordWrap(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        for widget in (
            self.di_label, self.di_button, self.folder_button, self.ir_list,
            self.loop, self.bypass, self.play_button, self.stop_button,
            self.position_label, self.progress, self.active_ir,
            self.favorite, self.rating, self.status,
        ):
            layout.addWidget(widget)
        self.setCentralWidget(container)
        self.di_button.clicked.connect(self.choose_di)
        self.folder_button.clicked.connect(self.choose_folder)
        self.ir_list.currentRowChanged.connect(self.selection_changed)
        self.play_button.clicked.connect(self.render)
        self.stop_button.clicked.connect(self.stop)
        self.loop.toggled.connect(self.output.set_loop)
        self.bypass.toggled.connect(self.selection_changed)
        self.favorite.toggled.connect(self.set_favorite)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.refresh_playback)
        self.timer.start()
        self.shortcuts = []
        for key, step in (("Left", -1), ("Right", 1)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda step=step: self.move_ir(step))
            self.shortcuts.append(shortcut)
        for key, action in (("Space", self.render), ("B", self.bypass.toggle)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(action)
            self.shortcuts.append(shortcut)
        favorite_shortcut = QShortcut(QKeySequence("F"), self)
        favorite_shortcut.setAutoRepeat(False)
        favorite_shortcut.activated.connect(self.toggle_favorite)
        self.shortcuts.append(favorite_shortcut)
        for value in range(1, 6):
            shortcut = QShortcut(QKeySequence(str(value)), self)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(lambda value=value: self.set_rating(value))
            self.shortcuts.append(shortcut)

    @Slot()
    def choose_di(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir DI", "", "WAV (*.wav *.WAV)")
        if filename:
            self.reset_audio()
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
            candidates = scan_wavs(root)
            metadata, errors = inspect_wavs(candidates)
            self.repository.upsert_many(metadata)
            paths = [item.path for item in metadata]
        except (OSError, ValueError) as error:
            self.show_error(str(error))
            return
        self.reset_audio()
        self.ir_list.clear()
        self.ir_paths = paths
        self.ir_list.addItems([str(path.relative_to(root)) for path in paths])
        skipped = f"; {len(errors)} inválidos ignorados" if errors else ""
        self.status.setText(
            f"{len(paths)} IRs válidos encontrados{skipped}; selecione um IR."
        )

    def reset_audio(self) -> None:
        self.cache = RenderCache()
        self.output.close()
        self.has_rendered_audio = False
        self.autoplay = True
        self.active_ir.setText("IR em reprodução: nenhum")

    def move_ir(self, step: int) -> None:
        row = self.ir_list.currentRow() + step
        if 0 <= row < self.ir_list.count():
            self.ir_list.setCurrentRow(row)

    @Slot()
    def selection_changed(self) -> None:
        self.selection_version += 1
        if self.ir_list.currentRow() < 0 and not self.bypass.isChecked():
            self.reset_audio()
        self.start_render()
        self.refresh_metadata()
        self.refresh_playback()
        self.update_play_button()

    def selected_ir_path(self) -> Path | None:
        row = self.ir_list.currentRow()
        return self.ir_paths[row] if 0 <= row < len(self.ir_paths) else None

    def refresh_metadata(self) -> None:
        path = self.selected_ir_path()
        item = self.repository.get(path) if path else None
        blocker = QSignalBlocker(self.favorite)
        self.favorite.setChecked(item.favorite if item else False)
        del blocker
        self.favorite.setEnabled(item is not None)
        rating = item.rating if item else 0
        self.rating.setText(f"Avaliação: {'★' * rating}{'☆' * (5 - rating)}")

    @Slot()
    def toggle_favorite(self) -> None:
        if self.favorite.isEnabled():
            self.favorite.toggle()

    @Slot(bool)
    def set_favorite(self, favorite: bool) -> None:
        path = self.selected_ir_path()
        if path is None:
            return
        try:
            self.repository.set_favorite(path, favorite)
            self.status.setText("Favorito atualizado.")
        except (KeyError, OSError) as error:
            self.show_error(str(error))
        self.refresh_metadata()

    def set_rating(self, rating: int) -> None:
        path = self.selected_ir_path()
        if path is None:
            return
        try:
            self.repository.set_rating(path, rating)
            self.status.setText(f"Avaliação definida como {rating}/5.")
        except (KeyError, OSError, ValueError) as error:
            self.show_error(str(error))
        self.refresh_metadata()

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
        self.play_button.setText(
            "Pause" if state == PlaybackState.PLAYING else
            "Play" if self.has_rendered_audio else "Processar e reproduzir"
        )

    @Slot()
    def update_play_button(self) -> None:
        self.play_button.setEnabled(
            self.has_rendered_audio or (
                self.worker is None and self.di_path is not None
                and (self.ir_list.currentRow() >= 0 or self.bypass.isChecked())
            )
        )

    @Slot()
    def render(self) -> None:
        row = self.ir_list.currentRow()
        if self.di_path is None or (row < 0 and not self.bypass.isChecked()):
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
        self.autoplay = True
        self.start_render()

    def start_render(self) -> None:
        row = self.ir_list.currentRow()
        if self.worker is not None or self.di_path is None or (row < 0 and not self.bypass.isChecked()):
            return
        self.worker_version = self.selection_version
        ir_path = None if self.bypass.isChecked() else self.ir_paths[row]
        self.worker = RenderWorker(self.di_path, ir_path, self.cache, self)
        self.worker.rendered.connect(self.play_rendered)
        self.worker.failed.connect(self.render_failed)
        self.worker.finished.connect(self.render_finished)
        self.set_busy(True)
        self.status.setText("Preparando DI…" if ir_path is None else "Processando DI + IR…")
        self.worker.start()

    @Slot(object)
    def play_rendered(self, audio: AudioBuffer) -> None:
        if self.worker_version != self.selection_version:
            return
        try:
            if self.has_rendered_audio:
                self.output.replace(audio)
            elif self.autoplay:
                self.output.play(audio, loop=self.loop.isChecked())
            else:
                self.output.load(audio)
                self.output.set_loop(self.loop.isChecked())
        except Exception as error:
            logger.exception("Unable to open audio output")
            self.show_error(str(error))
            return
        self.has_rendered_audio = True
        self.active_ir.setText(
            f"IR ativo: {self.worker.ir_path.name}" if self.worker.ir_path else "Bypass ativo: DI sem IR"
        )
        self.status.setText("Pause mantém a posição; Stop volta ao início.")

    @Slot(str)
    def render_failed(self, message: str) -> None:
        if self.worker_version == self.selection_version:
            self.show_error(message)

    @Slot()
    def render_finished(self) -> None:
        if self.worker is not None:
            self.worker.deleteLater()
        self.worker = None
        self.set_busy(False)
        self.refresh_playback()
        if self.worker_version != self.selection_version:
            self.start_render()

    def set_busy(self, busy: bool) -> None:
        for widget in (self.di_button, self.folder_button):
            widget.setEnabled(not busy)
        self.update_play_button()

    @Slot()
    def stop(self) -> None:
        self.autoplay = False
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
        self.repository.close()
        self.timer.stop()
        event.accept()
