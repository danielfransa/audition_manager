import logging
import sys

from PySide6.QtWidgets import QApplication

from audition_manager.audio.output import AudioOutput
from audition_manager.ui.fonts import configure_font
from audition_manager.ui.main_window import MainWindow


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    app = QApplication(sys.argv)
    app.setApplicationName("Audition Manager")
    try:
        configure_font(app)
    except RuntimeError as error:
        logging.getLogger(__name__).error("%s", error)
        return 1
    window = MainWindow(AudioOutput())
    window.show()
    return app.exec()
