from pathlib import Path


def scan_wavs(directory: Path) -> list[Path]:
    """Discover WAV candidates; decoding validates the selected candidate."""
    if not directory.is_dir():
        raise ValueError("Selecione um diretório existente.")
    return sorted(
        (path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() == ".wav"),
        key=lambda path: path.relative_to(directory).as_posix().casefold(),
    )
