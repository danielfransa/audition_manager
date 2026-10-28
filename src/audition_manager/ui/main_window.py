import logging
from pathlib import Path

from PySide6.QtCore import QSignalBlocker, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QPlainTextEdit,
    QSlider,
    QHBoxLayout,
    QInputDialog,
    QVBoxLayout,
    QWidget,
)

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.ir_processor import render_files
from audition_manager.audio.nam import NamRenderer, render_capture_chain, scan_nam_models
from audition_manager.audio.output import AudioOutput, OutputDevice
from audition_manager.audio.render_cache import RenderCache
from audition_manager.audio.transport import PlaybackState
from audition_manager.config.preferences import PreferencesStore
from audition_manager.library.scanner import inspect_wav, scan_wavs
from audition_manager.library.repository import ImpulseResponseRepository
from audition_manager.library.models import Capture
from audition_manager.library.exporter import export_files

logger = logging.getLogger(__name__)


def format_time(seconds: float) -> str:
    minutes, remainder = divmod(int(seconds), 60)
    return f"{minutes:02d}:{remainder:02d}"


def create_ir_directory_dialog(parent: QWidget, initial: str) -> QFileDialog:
    dialog = QFileDialog(parent, "Pasta de IRs", initial)
    dialog.setFileMode(QFileDialog.FileMode.Directory)
    dialog.setOption(QFileDialog.Option.ShowDirsOnly, False)
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    dialog.setNameFilter("Impulse Responses WAV (*.wav *.WAV)")
    dialog.setLabelText(
        QFileDialog.DialogLabel.Accept, "Escolher esta pasta"
    )
    return dialog


def choose_ir_directory(parent: QWidget, initial: str) -> str:
    dialog = create_ir_directory_dialog(parent, initial)
    if not dialog.exec():
        return ""
    selected = dialog.selectedFiles()
    return selected[0] if selected else ""


def choose_nam_directory(parent: QWidget, initial: str) -> str:
    dialog = QFileDialog(parent, "Pasta de capturas NAM", initial)
    dialog.setFileMode(QFileDialog.FileMode.Directory)
    dialog.setOption(QFileDialog.Option.ShowDirsOnly, False)
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    dialog.setNameFilter("Capturas NAM (*.nam *.NAM)")
    dialog.setLabelText(QFileDialog.DialogLabel.Accept, "Escolher esta pasta")
    if not dialog.exec():
        return ""
    selected = dialog.selectedFiles()
    return selected[0] if selected else ""


class StarRating(QWidget):
    rating_selected = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self._value = 0
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(QLabel("Avaliação:"))
        self.buttons: list[QPushButton] = []
        for value in range(1, 6):
            button = QPushButton("☆")
            button.setFlat(True)
            button.setFixedWidth(24)
            button.setToolTip(f"Definir avaliação como {value} de 5")
            button.setAccessibleName(f"{value} de 5 estrelas")
            button.clicked.connect(
                lambda _checked=False, value=value: self.rating_selected.emit(value)
            )
            layout.addWidget(button)
            self.buttons.append(button)

    def set_value(self, value: int) -> None:
        self._value = value
        for index, button in enumerate(self.buttons, start=1):
            button.setText("★" if index <= value else "☆")

    def text(self) -> str:
        return f"Avaliação: {'★' * self._value}{'☆' * (5 - self._value)}"


class RenderWorker(QThread):
    rendered = Signal(object)
    failed = Signal(str)

    def __init__(
        self, di_path: Path, ir_path: Path | None, cache: RenderCache, parent: QWidget,
        capture_path: Path | None = None, nam_renderer: NamRenderer | None = None,
    ) -> None:
        super().__init__(parent)
        self.di_path = di_path
        self.ir_path = ir_path
        self.cache = cache
        self.capture_path = capture_path
        self.nam_renderer = nam_renderer

    def run(self) -> None:
        try:
            if self.capture_path is None:
                audio = self.cache.render(self.di_path, self.ir_path, render_files)
            else:
                if self.nam_renderer is None:
                    raise RuntimeError("Runtime NAM não configurado.")
                audio = self.cache.render(
                    self.di_path,
                    self.ir_path,
                    lambda di, ir: render_capture_chain(
                        di, self.capture_path, ir, self.nam_renderer
                    ),
                    dependencies=(self.capture_path,),
                )
            self.rendered.emit(audio)
        except Exception as error:
            logger.exception("Unable to render audio")
            self.failed.emit(str(error))


class ScanWorker(QThread):
    progress = Signal(int, int)
    scanned = Signal(object, object, object)
    failed = Signal(object, str)
    cancelled = Signal(object)

    def __init__(self, root: Path, parent: QWidget) -> None:
        super().__init__(parent)
        self.root = root.resolve()

    def run(self) -> None:
        try:
            candidates = scan_wavs(self.root)
            total = len(candidates)
            items = []
            errors = []
            self.progress.emit(0, total)
            for index, path in enumerate(candidates, start=1):
                if self.isInterruptionRequested():
                    self.cancelled.emit(self.root)
                    return
                try:
                    items.append(inspect_wav(path))
                except Exception as error:
                    errors.append((path, str(error)))
                self.progress.emit(index, total)
            if self.isInterruptionRequested():
                self.cancelled.emit(self.root)
                return
            self.scanned.emit(self.root, items, errors)
        except Exception as error:
            logger.exception("Unable to scan IR directory")
            self.failed.emit(self.root, str(error))


class MainWindow(QMainWindow):
    def __init__(
        self,
        output: AudioOutput,
        repository: ImpulseResponseRepository,
        preferences_store: PreferencesStore,
        nam_renderer: NamRenderer | None = None,
    ) -> None:
        super().__init__()
        self.output = output
        self.repository = repository
        self.preferences_store = preferences_store
        self.preferences = preferences_store.load()
        self.nam_renderer = nam_renderer or NamRenderer()
        self.di_path: Path | None = None
        self.ir_root: Path | None = None
        self.all_ir_paths: list[Path] = []
        self.ir_paths: list[Path] = []
        self.capture_root: Path | None = None
        self.all_capture_paths: list[Path] = []
        self.capture_paths: list[Path] = []
        self.worker: RenderWorker | None = None
        self.scan_worker: ScanWorker | None = None
        self.desired_scan_root: Path | None = None
        self.applied_scan_root: Path | None = None
        self.close_after_scan = False
        self.cache = RenderCache()
        self.has_rendered_audio = False
        self.selection_version = 0
        self.worker_version = -1
        self.autoplay = True
        self.setWindowTitle("Audition Manager")
        self.resize(820, 700)
        self.di_label = QLabel("Nenhuma DI selecionada")
        self.di_button = QPushButton("Abrir DI WAV")
        self.folder_button = QPushButton("Selecionar pasta de IRs")
        self.capture_button = QPushButton("Selecionar pasta de capturas NAM")
        self.clear_capture_button = QPushButton("Sem captura")
        self.capture_list = QListWidget()
        self.capture_list.setMaximumHeight(150)
        self.capture_list.setToolTip("Opcional: selecione uma captura antes do IR")
        self.capture_search = QLineEdit()
        self.capture_search.setPlaceholderText("Buscar captura por nome ou caminho…")
        self.capture_favorites_only = QCheckBox("Somente capturas favoritas")
        self.capture_minimum_rating = QComboBox()
        self.capture_minimum_rating.addItem("Todas as avaliações", 0)
        for value in range(1, 6):
            self.capture_minimum_rating.addItem(f"{value}+ estrelas", value)
        self.capture_favorite = QCheckBox("Captura favorita")
        self.capture_favorite.setEnabled(False)
        self.capture_rating = StarRating()
        self.capture_rating.setEnabled(False)
        self.capture_notes = QPlainTextEdit()
        self.capture_notes.setPlaceholderText("Notas sobre a captura selecionada…")
        self.capture_notes.setMaximumHeight(70)
        self.capture_notes.setEnabled(False)
        self.save_capture_notes_button = QPushButton("Salvar notas da captura")
        self.save_capture_notes_button.setEnabled(False)
        self.export_button = QPushButton("Exportar favoritos…")
        self.export_button.setEnabled(False)
        self.cancel_scan_button = QPushButton("Cancelar scan")
        self.cancel_scan_button.setEnabled(False)
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar IR por nome ou caminho…")
        self.favorites_only = QCheckBox("Somente favoritos")
        self.minimum_rating = QComboBox()
        self.minimum_rating.addItem("Todas as avaliações", 0)
        for value in range(1, 6):
            self.minimum_rating.addItem(f"{value}+ estrelas", value)
        self.ir_list = QListWidget()
        self.device = QComboBox()
        self.device.setToolTip("Dispositivo de saída")
        self.gain = QSlider(Qt.Orientation.Horizontal)
        self.gain.setRange(-24, 0)
        self.gain.setValue(self.preferences.output_gain_db)
        self.gain_label = QLabel(
            f"Ganho de saída: {self.preferences.output_gain_db} dB"
        )
        self.bypass = QCheckBox("Bypass IR (B)")
        self.capture_bypass = QCheckBox("Bypass captura NAM (N)")
        self.loop = QCheckBox("Loop")
        self.loop.setChecked(self.preferences.loop_enabled)
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
        self.rating = StarRating()
        self.rating.setEnabled(False)
        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText("Notas sobre o IR selecionado…")
        self.notes.setMaximumHeight(90)
        self.notes.setEnabled(False)
        self.save_notes_button = QPushButton("Salvar notas")
        self.save_notes_button.setEnabled(False)
        self.status = QLabel("Abra uma DI e selecione um IR.")
        self.status.setWordWrap(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.di_label)
        file_buttons = QHBoxLayout()
        file_buttons.addWidget(self.di_button)
        file_buttons.addWidget(self.folder_button)
        file_buttons.addWidget(self.export_button)
        file_buttons.addWidget(self.cancel_scan_button)
        layout.addLayout(file_buttons)
        capture_buttons = QHBoxLayout()
        capture_buttons.addWidget(self.capture_button)
        capture_buttons.addWidget(self.clear_capture_button)
        layout.addLayout(capture_buttons)
        layout.addWidget(QLabel("Captura NAM (opcional):"))
        capture_filters = QHBoxLayout()
        capture_filters.addWidget(self.capture_search, 1)
        capture_filters.addWidget(self.capture_favorites_only)
        capture_filters.addWidget(self.capture_minimum_rating)
        layout.addLayout(capture_filters)
        layout.addWidget(self.capture_list)
        capture_metadata = QHBoxLayout()
        capture_metadata.addWidget(self.capture_favorite)
        capture_metadata.addWidget(self.capture_rating)
        capture_metadata.addStretch(1)
        layout.addLayout(capture_metadata)
        layout.addWidget(self.capture_notes)
        layout.addWidget(self.save_capture_notes_button)
        layout.addWidget(self.scan_progress)
        layout.addWidget(self.device)
        gain_row = QHBoxLayout()
        gain_row.addWidget(self.gain_label)
        gain_row.addWidget(self.gain, 1)
        layout.addLayout(gain_row)
        filters = QHBoxLayout()
        filters.addWidget(self.search, 1)
        filters.addWidget(self.favorites_only)
        filters.addWidget(self.minimum_rating)
        layout.addLayout(filters)
        layout.addWidget(self.ir_list, 1)
        transport = QHBoxLayout()
        transport.addWidget(self.loop)
        transport.addWidget(self.bypass)
        transport.addWidget(self.capture_bypass)
        transport.addWidget(self.play_button, 1)
        transport.addWidget(self.stop_button)
        layout.addLayout(transport)
        layout.addWidget(self.position_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.active_ir)
        metadata = QHBoxLayout()
        metadata.addWidget(self.favorite)
        metadata.addWidget(self.rating)
        metadata.addStretch(1)
        layout.addLayout(metadata)
        layout.addWidget(self.notes)
        layout.addWidget(self.save_notes_button)
        layout.addWidget(self.status)
        self.setCentralWidget(container)
        self.di_button.clicked.connect(self.choose_di)
        self.folder_button.clicked.connect(self.choose_folder)
        self.capture_button.clicked.connect(self.choose_capture_folder)
        self.clear_capture_button.clicked.connect(self.clear_capture_selection)
        self.capture_list.currentRowChanged.connect(self.selection_changed)
        self.capture_search.textChanged.connect(self.apply_capture_filters)
        self.capture_favorites_only.toggled.connect(self.apply_capture_filters)
        self.capture_minimum_rating.currentIndexChanged.connect(
            self.apply_capture_filters
        )
        self.capture_favorite.toggled.connect(self.set_capture_favorite)
        self.capture_rating.rating_selected.connect(self.set_capture_rating)
        self.save_capture_notes_button.clicked.connect(self.save_capture_notes)
        self.export_button.clicked.connect(self.export_favorites)
        self.cancel_scan_button.clicked.connect(self.cancel_scan)
        self.device.currentIndexChanged.connect(self.change_device)
        self.gain.valueChanged.connect(self.change_gain)
        self.search.textChanged.connect(self.apply_filters)
        self.favorites_only.toggled.connect(self.apply_filters)
        self.minimum_rating.currentIndexChanged.connect(self.apply_filters)
        self.ir_list.currentRowChanged.connect(self.selection_changed)
        self.play_button.clicked.connect(self.render)
        self.stop_button.clicked.connect(self.stop)
        self.loop.toggled.connect(self.change_loop)
        self.bypass.toggled.connect(self.selection_changed)
        self.capture_bypass.toggled.connect(self.selection_changed)
        self.favorite.toggled.connect(self.set_favorite)
        self.rating.rating_selected.connect(self.set_rating)
        self.save_notes_button.clicked.connect(self.save_notes)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.refresh_playback)
        self.timer.start()
        self.shortcuts = []
        for key, step in (("Left", -1), ("Right", 1)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda step=step: self.move_ir(step))
            self.shortcuts.append(shortcut)
        for key, step in (("Ctrl+Left", -1), ("Ctrl+Right", 1)):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(lambda step=step: self.move_capture(step))
            self.shortcuts.append(shortcut)
        self.refresh_devices()
        self.output.set_gain_db(self.gain.value())
        self.output.set_loop(self.loop.isChecked())
        for key, action in (
            ("Space", self.toggle_playback_shortcut),
            ("B", self.toggle_bypass_shortcut),
            ("N", self.toggle_capture_bypass_shortcut),
        ):
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(action)
            self.shortcuts.append(shortcut)
        favorite_shortcut = QShortcut(QKeySequence("F"), self)
        favorite_shortcut.setAutoRepeat(False)
        favorite_shortcut.activated.connect(self.toggle_favorite)
        self.shortcuts.append(favorite_shortcut)
        for value in range(0, 6):
            shortcut = QShortcut(QKeySequence(str(value)), self)
            shortcut.setAutoRepeat(False)
            shortcut.activated.connect(lambda value=value: self.set_rating(value))
            self.shortcuts.append(shortcut)
        self.restore_paths()

    @Slot()
    def choose_di(self) -> None:
        initial = str(self.di_path.parent) if self.di_path else ""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Abrir DI", initial, "WAV (*.wav *.WAV)"
        )
        if filename:
            self.reset_audio()
            self.di_path = Path(filename)
            self.di_label.setText(f"DI: {self.di_path.name}")
            self.preferences.last_di_file = self.di_path.resolve()
            self.save_preferences()
            self.selection_changed()

    @Slot()
    def choose_folder(self) -> None:
        initial = str(self.ir_root or self.preferences.last_ir_directory or "")
        directory = choose_ir_directory(self, initial)
        if not directory:
            return
        self.begin_scan(Path(directory))

    @Slot()
    def choose_capture_folder(self) -> None:
        initial = str(
            self.capture_root or self.preferences.last_capture_directory or ""
        )
        directory = choose_nam_directory(self, initial)
        if not directory:
            return
        self.open_capture_folder(Path(directory))

    def open_capture_folder(self, directory: Path) -> None:
        root = directory.resolve()
        models, errors = scan_nam_models(root)
        captures = [Capture(
            model.path, model.path.name, model.version, model.architecture,
            model.sample_rate, model.submodel_count,
        ) for model in models]
        self.repository.upsert_captures(captures)
        self.capture_root = root
        self.all_capture_paths = [model.path for model in models]
        self.preferences.last_capture_directory = root
        self.save_preferences()
        self.apply_capture_filters()
        skipped = f"; {len(errors)} inválidas ignoradas" if errors else ""
        self.status.setText(
            f"{len(models)} capturas NAM A2 encontradas{skipped}."
        )
        saved = self.preferences.last_capture_file
        if saved in self.capture_paths:
            self.capture_list.setCurrentRow(self.capture_paths.index(saved))

    @Slot()
    def clear_capture_selection(self) -> None:
        blocker = QSignalBlocker(self.capture_list)
        self.capture_list.setCurrentRow(-1)
        del blocker
        self.preferences.last_capture_file = None
        self.save_preferences()
        self.selection_changed()

    def capture_item_text(self, path: Path) -> str:
        item = self.repository.get_capture(path)
        relative = str(path.relative_to(self.capture_root)) if self.capture_root else path.name
        if item is None:
            return relative
        favorite = "★ " if item.favorite else ""
        rating = f" [{'★' * item.rating}{'☆' * (5 - item.rating)}]"
        return f"{favorite}{relative}{rating}"

    @Slot()
    def apply_capture_filters(self) -> None:
        selected = self.selected_capture_path()
        query = self.capture_search.text().strip().casefold()
        minimum = self.capture_minimum_rating.currentData() or 0
        visible = []
        for path in self.all_capture_paths:
            item = self.repository.get_capture(path)
            if item is None:
                continue
            relative = str(path.relative_to(self.capture_root)) if self.capture_root else path.name
            if query and query not in relative.casefold():
                continue
            if self.capture_favorites_only.isChecked() and not item.favorite:
                continue
            if item.rating < minimum:
                continue
            visible.append(path)
        blocker = QSignalBlocker(self.capture_list)
        self.capture_list.clear()
        self.capture_paths = visible
        self.capture_list.addItems([self.capture_item_text(path) for path in visible])
        if selected in visible:
            self.capture_list.setCurrentRow(visible.index(selected))
        del blocker
        self.refresh_capture_metadata()
        if selected is not None and selected not in visible:
            self.selection_changed()

    def begin_scan(self, root: Path) -> None:
        try:
            resolved = root.resolve(strict=True)
        except OSError as error:
            self.show_error(str(error))
            return
        if not resolved.is_dir():
            self.show_error("Selecione um diretório existente.")
            return
        self.desired_scan_root = resolved
        if self.scan_worker is not None:
            self.scan_worker.requestInterruption()
            self.status.setText("Cancelando scan anterior para abrir a nova pasta…")
            return
        self.start_scan(resolved)

    def start_scan(self, root: Path) -> None:
        self.scan_worker = ScanWorker(root, self)
        self.scan_worker.progress.connect(self.update_scan_progress)
        self.scan_worker.scanned.connect(self.scan_completed)
        self.scan_worker.failed.connect(self.scan_failed)
        self.scan_worker.cancelled.connect(self.scan_cancelled)
        self.scan_worker.finished.connect(self.scan_finished)
        self.cancel_scan_button.setEnabled(True)
        self.scan_progress.setRange(0, 0)
        self.scan_progress.setVisible(True)
        self.status.setText(f"Escaneando IRs em {root}…")
        self.scan_worker.start()

    @Slot(int, int)
    def update_scan_progress(self, current: int, total: int) -> None:
        self.scan_progress.setRange(0, total or 0)
        if total:
            self.scan_progress.setValue(current)
            self.scan_progress.setFormat(f"Analisando IRs: {current}/{total}")

    @Slot(object, object, object)
    def scan_completed(self, root: Path, metadata: list, errors: list) -> None:
        if root != self.desired_scan_root:
            return
        try:
            self.repository.upsert_many(metadata)
        except Exception as error:
            self.show_error(str(error))
            self.desired_scan_root = None
            return
        self.reset_audio()
        self.ir_root = root
        self.all_ir_paths = [item.path for item in metadata]
        self.applied_scan_root = root
        self.preferences.last_ir_directory = root
        self.save_preferences()
        self.apply_filters()
        skipped = f"; {len(errors)} inválidos ignorados" if errors else ""
        self.status.setText(
            f"{len(metadata)} IRs válidos encontrados{skipped}; selecione um IR."
        )

    @Slot(object, str)
    def scan_failed(self, root: Path, message: str) -> None:
        if root == self.desired_scan_root:
            self.desired_scan_root = None
            self.show_error(message)

    @Slot(object)
    def scan_cancelled(self, root: Path) -> None:
        if self.desired_scan_root is None or root == self.desired_scan_root:
            self.status.setText("Scan cancelado; a biblioteca anterior foi mantida.")

    @Slot()
    def scan_finished(self) -> None:
        if self.scan_worker is not None:
            self.scan_worker.deleteLater()
        self.scan_worker = None
        self.cancel_scan_button.setEnabled(False)
        self.scan_progress.setVisible(False)
        if self.close_after_scan:
            self.close_after_scan = False
            self.close()
            return
        if (
            self.desired_scan_root is not None
            and self.desired_scan_root != self.applied_scan_root
        ):
            self.start_scan(self.desired_scan_root)

    @Slot()
    def cancel_scan(self) -> None:
        self.desired_scan_root = None
        if self.scan_worker is not None:
            self.scan_worker.requestInterruption()
            self.status.setText("Cancelando scan…")

    def reset_audio(self) -> None:
        self.cache = RenderCache()
        self.output.close()
        self.has_rendered_audio = False
        self.autoplay = True
        self.active_ir.setText("IR em reprodução: nenhum")

    def move_ir(self, step: int) -> None:
        if self.notes.hasFocus():
            return
        row = self.ir_list.currentRow() + step
        if 0 <= row < self.ir_list.count():
            self.ir_list.setCurrentRow(row)

    def move_capture(self, step: int) -> None:
        if self.capture_notes.hasFocus():
            return
        row = self.capture_list.currentRow() + step
        if 0 <= row < self.capture_list.count():
            self.capture_list.setCurrentRow(row)

    def toggle_playback_shortcut(self) -> None:
        if not self.notes.hasFocus():
            self.render()

    def toggle_bypass_shortcut(self) -> None:
        if not self.notes.hasFocus():
            self.bypass.toggle()

    def toggle_capture_bypass_shortcut(self) -> None:
        if not self.notes.hasFocus():
            self.capture_bypass.toggle()

    def item_text(self, path: Path) -> str:
        item = self.repository.get(path)
        relative = str(path.relative_to(self.ir_root)) if self.ir_root else path.name
        if item is None:
            return relative
        favorite = "★ " if item.favorite else ""
        rating = f" [{'★' * item.rating}{'☆' * (5 - item.rating)}]"
        return f"{favorite}{relative}{rating}"

    @Slot()
    def apply_filters(self) -> None:
        selected = self.selected_ir_path()
        query = self.search.text().strip().casefold()
        minimum = self.minimum_rating.currentData() or 0
        visible: list[Path] = []
        for path in self.all_ir_paths:
            item = self.repository.get(path)
            if item is None:
                continue
            relative = str(path.relative_to(self.ir_root)) if self.ir_root else path.name
            if query and query not in relative.casefold():
                continue
            if self.favorites_only.isChecked() and not item.favorite:
                continue
            if item.rating < minimum:
                continue
            visible.append(path)
        blocker = QSignalBlocker(self.ir_list)
        self.ir_list.clear()
        self.ir_paths = visible
        self.ir_list.addItems([self.item_text(path) for path in visible])
        if selected in visible:
            self.ir_list.setCurrentRow(visible.index(selected))
        del blocker
        self.refresh_metadata()
        self.export_button.setEnabled(bool(self.favorite_paths()))
        self.update_play_button()

    def favorite_paths(self) -> list[Path]:
        return [
            path for path in self.all_ir_paths
            if (item := self.repository.get(path)) is not None and item.favorite
        ]

    @Slot()
    def export_favorites(self) -> None:
        if self.ir_root is None:
            self.status.setText("Selecione uma pasta de IRs antes de exportar.")
            return
        favorites = self.favorite_paths()
        if not favorites:
            self.status.setText("Marque ao menos um IR como favorito.")
            return
        parent = QFileDialog.getExistingDirectory(
            self,
            "Local para criar a pasta de favoritos",
            str(self.preferences.last_export_directory or ""),
        )
        if not parent:
            return
        name, accepted = QInputDialog.getText(
            self, "Nome da pasta", "Nome da nova pasta:",
            text="Audition Manager Favorites",
        )
        if not accepted:
            return
        try:
            result = export_files(self.ir_root, favorites, Path(parent), name)
        except (OSError, ValueError) as error:
            self.show_error(str(error))
            return
        message = f"{result.file_count} favoritos exportados para {result.directory}"
        self.preferences.last_export_directory = Path(parent).resolve()
        self.save_preferences()
        self.status.setText(message)
        QMessageBox.information(self, "Exportação concluída", message)

    def refresh_devices(self) -> None:
        blocker = QSignalBlocker(self.device)
        self.device.clear()
        self.device.addItem("Saída padrão do sistema", None)
        selected_index = 0
        try:
            for device in self.output.list_devices():
                self.device.addItem(
                    f"{device.name} — {device.host_api}", device
                )
                if (
                    device.name == self.preferences.output_device_name
                    and device.host_api == self.preferences.output_host_api
                ):
                    selected_index = self.device.count() - 1
        except Exception as error:
            logger.exception("Unable to enumerate output devices")
            self.status.setText(f"Não foi possível listar saídas de áudio: {error}")
        self.device.setCurrentIndex(selected_index)
        del blocker
        if selected_index == 0 and self.preferences.output_device_name is not None:
            self.preferences.output_device_name = None
            self.preferences.output_host_api = None
            self.save_preferences()
        self.apply_device(save=False)

    @Slot(int)
    def change_device(self, _index: int) -> None:
        self.apply_device(save=True)

    def apply_device(self, *, save: bool) -> None:
        device: OutputDevice | None = self.device.currentData()
        try:
            self.output.set_device(device.index if device else None)
            self.status.setText(f"Saída: {self.device.currentText()}.")
            if save:
                self.preferences.output_device_name = device.name if device else None
                self.preferences.output_host_api = device.host_api if device else None
                self.save_preferences()
        except Exception as error:
            logger.exception("Unable to change output device")
            self.show_error(str(error))
        self.refresh_playback()

    @Slot(int)
    def change_gain(self, gain_db: int) -> None:
        try:
            self.output.set_gain_db(gain_db)
            self.gain_label.setText(f"Ganho de saída: {gain_db} dB")
            self.preferences.output_gain_db = gain_db
            self.save_preferences()
        except ValueError as error:
            self.show_error(str(error))

    @Slot(bool)
    def change_loop(self, enabled: bool) -> None:
        self.output.set_loop(enabled)
        self.preferences.loop_enabled = enabled
        self.save_preferences()

    def restore_paths(self) -> None:
        changed = False
        di_path = self.preferences.last_di_file
        if di_path is not None and di_path.is_file():
            self.di_path = di_path.resolve()
            self.di_label.setText(f"DI: {self.di_path.name}")
        elif di_path is not None:
            self.preferences.last_di_file = None
            changed = True
        ir_directory = self.preferences.last_ir_directory
        if ir_directory is not None and ir_directory.is_dir():
            self.begin_scan(ir_directory)
        elif ir_directory is not None:
            self.preferences.last_ir_directory = None
            changed = True
        capture_directory = self.preferences.last_capture_directory
        if capture_directory is not None and capture_directory.is_dir():
            self.open_capture_folder(capture_directory)
        elif capture_directory is not None:
            self.preferences.last_capture_directory = None
            self.preferences.last_capture_file = None
            changed = True
        export_directory = self.preferences.last_export_directory
        if export_directory is not None and not export_directory.is_dir():
            self.preferences.last_export_directory = None
            changed = True
        if changed:
            self.save_preferences()

    def save_preferences(self) -> None:
        try:
            self.preferences_store.save(self.preferences)
        except OSError as error:
            logger.exception("Unable to save preferences")
            self.status.setText(f"Não foi possível salvar as preferências: {error}")

    @Slot()
    def selection_changed(self) -> None:
        self.selection_version += 1
        capture = self.selected_capture_path()
        if capture != self.preferences.last_capture_file:
            self.preferences.last_capture_file = capture
            self.save_preferences()
        if self.ir_list.currentRow() < 0 and not self.bypass.isChecked():
            self.reset_audio()
        self.start_render()
        self.refresh_metadata()
        self.refresh_capture_metadata()
        self.refresh_playback()
        self.update_play_button()

    def selected_ir_path(self) -> Path | None:
        row = self.ir_list.currentRow()
        return self.ir_paths[row] if 0 <= row < len(self.ir_paths) else None

    def selected_capture_path(self) -> Path | None:
        row = self.capture_list.currentRow()
        return self.capture_paths[row] if 0 <= row < len(self.capture_paths) else None

    def refresh_metadata(self) -> None:
        path = self.selected_ir_path()
        item = self.repository.get(path) if path else None
        blocker = QSignalBlocker(self.favorite)
        self.favorite.setChecked(item.favorite if item else False)
        del blocker
        self.favorite.setEnabled(item is not None)
        rating = item.rating if item else 0
        self.rating.set_value(rating)
        self.rating.setEnabled(item is not None)
        notes_blocker = QSignalBlocker(self.notes)
        self.notes.setPlainText(item.notes if item else "")
        del notes_blocker
        self.notes.setEnabled(item is not None)
        self.save_notes_button.setEnabled(item is not None)

    def refresh_capture_metadata(self) -> None:
        path = self.selected_capture_path()
        item = self.repository.get_capture(path) if path else None
        blocker = QSignalBlocker(self.capture_favorite)
        self.capture_favorite.setChecked(item.favorite if item else False)
        del blocker
        self.capture_favorite.setEnabled(item is not None)
        self.capture_rating.set_value(item.rating if item else 0)
        self.capture_rating.setEnabled(item is not None)
        notes_blocker = QSignalBlocker(self.capture_notes)
        self.capture_notes.setPlainText(item.notes if item else "")
        del notes_blocker
        self.capture_notes.setEnabled(item is not None)
        self.save_capture_notes_button.setEnabled(item is not None)

    @Slot(bool)
    def set_capture_favorite(self, favorite: bool) -> None:
        path = self.selected_capture_path()
        if path is None:
            return
        try:
            self.repository.set_capture_favorite(path, favorite)
            self.status.setText("Favorito da captura atualizado.")
        except (KeyError, OSError) as error:
            self.show_error(str(error))
        self.apply_capture_filters()

    def set_capture_rating(self, rating: int) -> None:
        path = self.selected_capture_path()
        if path is None:
            return
        try:
            self.repository.set_capture_rating(path, rating)
            self.status.setText(f"Avaliação da captura definida como {rating}/5.")
        except (KeyError, OSError, ValueError) as error:
            self.show_error(str(error))
        self.apply_capture_filters()

    @Slot()
    def save_capture_notes(self) -> None:
        path = self.selected_capture_path()
        if path is None:
            return
        try:
            self.repository.set_capture_notes(path, self.capture_notes.toPlainText())
            self.status.setText("Notas da captura salvas.")
        except (KeyError, OSError) as error:
            self.show_error(str(error))

    @Slot()
    def toggle_favorite(self) -> None:
        if not self.notes.hasFocus() and self.favorite.isEnabled():
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
        self.apply_filters()

    def set_rating(self, rating: int) -> None:
        if self.notes.hasFocus():
            return
        path = self.selected_ir_path()
        if path is None:
            return
        try:
            self.repository.set_rating(path, rating)
            self.status.setText(f"Avaliação definida como {rating}/5.")
        except (KeyError, OSError, ValueError) as error:
            self.show_error(str(error))
        self.apply_filters()

    @Slot()
    def save_notes(self) -> None:
        path = self.selected_ir_path()
        if path is None:
            return
        try:
            self.repository.set_notes(path, self.notes.toPlainText())
            self.status.setText("Notas salvas.")
        except (KeyError, OSError) as error:
            self.show_error(str(error))

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
        capture_path = (
            None if self.capture_bypass.isChecked()
            else self.selected_capture_path()
        )
        self.worker = RenderWorker(
            self.di_path, ir_path, self.cache, self, capture_path, self.nam_renderer
        )
        self.worker.rendered.connect(self.play_rendered)
        self.worker.failed.connect(self.render_failed)
        self.worker.finished.connect(self.render_finished)
        self.set_busy(True)
        stages = ["DI"]
        if capture_path is not None:
            stages.append("NAM")
        if ir_path is not None:
            stages.append("IR")
        self.status.setText(f"Processando {' + '.join(stages)}…")
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
        active = []
        if self.worker.capture_path is not None:
            active.append(self.worker.capture_path.name)
        if self.worker.ir_path is not None:
            active.append(self.worker.ir_path.name)
        self.active_ir.setText(
            f"Ativo: {' → '.join(active)}" if active else "Bypass ativo: DI limpa"
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
        for widget in (self.di_button, self.folder_button, self.capture_button):
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
        if self.scan_worker is not None:
            self.close_after_scan = True
            self.cancel_scan()
            self.status.setText("Cancelando scan antes de fechar…")
            event.ignore()
            return
        self.save_preferences()
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
