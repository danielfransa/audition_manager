"""Export selected library files without device-specific transfer logic."""

from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from tempfile import TemporaryDirectory


INVALID_WINDOWS_CHARACTERS = set('<>:"/\\|?*')
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


@dataclass(frozen=True)
class ExportResult:
    directory: Path
    file_count: int
    total_bytes: int


def validate_folder_name(name: str) -> str:
    candidate = name.strip()
    if not candidate or candidate in {".", ".."}:
        raise ValueError("Informe um nome para a pasta de exportação.")
    if candidate != name or any(char in INVALID_WINDOWS_CHARACTERS for char in candidate):
        raise ValueError(
            "O nome não pode começar/terminar com espaços nem conter < > : \" / \\ | ? *."
        )
    if candidate.endswith(".") or any(ord(char) < 32 for char in candidate):
        raise ValueError("O nome da pasta contém caracteres inválidos.")
    if candidate.split(".", 1)[0].upper() in WINDOWS_RESERVED_NAMES:
        raise ValueError("Esse nome é reservado pelo Windows.")
    return candidate


def export_files(
    source_root: Path,
    sources: list[Path],
    destination_parent: Path,
    folder_name: str,
) -> ExportResult:
    name = validate_folder_name(folder_name)
    root = source_root.resolve(strict=True)
    parent = destination_parent.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError("Selecione um diretório de destino existente.")
    target = parent / name
    try:
        target.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError(
            "Escolha um destino fora da pasta de IRs para evitar cópias duplicadas no scan."
        )
    if target.exists():
        raise FileExistsError(f"A pasta de exportação já existe: {target}")
    if not sources:
        raise ValueError("Nenhum IR favorito disponível para exportação.")

    entries: list[tuple[Path, Path]] = []
    total_bytes = 0
    for source in sources:
        resolved = source.resolve(strict=True)
        if not resolved.is_file():
            raise ValueError(f"O favorito não é um arquivo: {resolved}")
        try:
            relative = resolved.relative_to(root)
        except ValueError as error:
            raise ValueError(f"O favorito está fora da pasta de IRs: {resolved}") from error
        entries.append((resolved, relative))
        total_bytes += resolved.stat().st_size

    with TemporaryDirectory(prefix=".audition-manager-export-", dir=parent) as staging:
        payload = Path(staging) / name
        payload.mkdir()
        for source, relative in entries:
            destination = payload / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            copy2(source, destination)
        payload.rename(target)
    return ExportResult(target, len(entries), total_bytes)
