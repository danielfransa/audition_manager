import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from audition_manager.audio.output import AudioOutput
from audition_manager.audio.nam import NamRenderer
from audition_manager.config.preferences import PreferencesStore
from audition_manager.config.settings import database_path, preferences_path
from audition_manager.library.repository import ImpulseResponseRepository
from audition_manager.ui.fonts import configure_font
from audition_manager.ui.main_window import MainWindow


def packaging_smoke_test() -> int:
    """Validate imports and files that must exist in a frozen distribution."""
    renderer = NamRenderer().executable
    if not renderer.is_file():
        logging.getLogger(__name__).error("Runtime NAM ausente: %s", renderer)
        return 1
    if not Path(sys.executable).is_file():
        logging.getLogger(__name__).error("Executável da aplicação ausente.")
        return 1
    return 0


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    if "--packaging-smoke-test" in sys.argv:
        return packaging_smoke_test()
    app = QApplication(sys.argv)
    app.setApplicationName("Audition Manager")
    try:
        configure_font(app)
    except RuntimeError as error:
        logging.getLogger(__name__).error("%s", error)
        return 1
    window = MainWindow(
        AudioOutput(),
        ImpulseResponseRepository(database_path()),
        PreferencesStore(preferences_path()),
    )
    window.show()
    return app.exec()
