from pathlib import Path

import soundfile as sf

from audition_manager.library.models import ImpulseResponse


def scan_wavs(directory: Path) -> list[Path]:
    """Discover WAV candidates; decoding validates the selected candidate."""
    if not directory.is_dir():
        raise ValueError("Selecione um diretório existente.")
    return sorted(
        (path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() == ".wav"),
        key=lambda path: path.relative_to(directory).as_posix().casefold(),
    )


def inspect_wavs(paths: list[Path]) -> tuple[list[ImpulseResponse], list[tuple[Path, str]]]:
    items: list[ImpulseResponse] = []
    errors: list[tuple[Path, str]] = []
    for path in paths:
        try:
            info = sf.info(path)
            items.append(ImpulseResponse(path.resolve(), path.name, info.samplerate, info.channels))
        except (OSError, RuntimeError, sf.LibsndfileError) as error:
            errors.append((path, str(error)))
    return items, errors
