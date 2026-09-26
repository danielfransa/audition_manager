"""Select a readable system font before creating any widgets."""

from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics
from PySide6.QtWidgets import QApplication


def configure_font(app: QApplication) -> None:
    sample = "Audition Manager Reprodução seleção … 0123456789"
    fonts = [app.font()]
    families = QFontDatabase.families(QFontDatabase.WritingSystem.Latin)
    preferred = ["Segoe UI", "Noto Sans", "DejaVu Sans", "Liberation Sans"]
    for family in dict.fromkeys(preferred + families):
        if family in families:
            fonts.append(QFont(family, 10))
    for font in fonts:
        metrics = QFontMetrics(font)
        if all(metrics.inFontUcs4(ord(char)) for char in sample):
            app.setFont(font)
            return
    raise RuntimeError(
        "Nenhuma fonte legível disponível para a interface. "
        "No Arch Linux/WSL, instale: sudo pacman -S --needed ttf-dejavu. "
        "Depois execute fc-cache -f e reabra o aplicativo. "
        "Em outros sistemas, instale ou restaure uma fonte como DejaVu Sans."
    )
