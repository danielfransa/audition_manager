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


@dataclass(frozen=True)
class FavoriteExportResult:
    directory: Path
    ir_count: int
    capture_count: int
    total_bytes: int

    @property
    def file_count(self) -> int:
        return self.ir_count + self.capture_count


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


def export_library_favorites(
    destination_parent: Path,
    folder_name: str,
    *,
    ir_root: Path | None = None,
    ir_sources: list[Path] | None = None,
    capture_root: Path | None = None,
    capture_sources: list[Path] | None = None,
) -> FavoriteExportResult:
    """Export favorites atomically into separate IRs and Capturas directories."""
    name = validate_folder_name(folder_name)
    parent = destination_parent.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError("Selecione um diretório de destino existente.")
    target = parent / name
    if target.exists():
        raise FileExistsError(f"A pasta de exportação já existe: {target}")

    ir_entries = _collect_entries(ir_root, ir_sources or [], "IR")
    capture_entries = _collect_entries(
        capture_root, capture_sources or [], "captura"
    )
    if not ir_entries and not capture_entries:
        raise ValueError("Nenhum IR ou captura favorito disponível para exportação.")
    for root in (ir_root, capture_root):
        if root is None:
            continue
        try:
            target.relative_to(root.resolve(strict=True))
        except ValueError:
            continue
        raise ValueError("Escolha um destino fora das bibliotecas abertas.")

    total_bytes = sum(
        source.stat().st_size
        for source, _relative in [*ir_entries, *capture_entries]
    )
    with TemporaryDirectory(prefix=".audition-manager-export-", dir=parent) as staging:
        payload = Path(staging) / name
        ir_directory = payload / "IRs"
        capture_directory = payload / "Capturas"
        ir_directory.mkdir(parents=True)
        capture_directory.mkdir(parents=True)
        for directory, entries in (
            (ir_directory, ir_entries), (capture_directory, capture_entries)
        ):
            for source, relative in entries:
                destination = directory / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                copy2(source, destination)
        payload.rename(target)
    return FavoriteExportResult(
        target, len(ir_entries), len(capture_entries), total_bytes
    )


def _collect_entries(
    root: Path | None, sources: list[Path], kind: str
) -> list[tuple[Path, Path]]:
    if not sources:
        return []
    if root is None:
        raise ValueError(f"A pasta de {kind}s não está aberta.")
    resolved_root = root.resolve(strict=True)
    entries = []
    for source in sources:
        resolved = source.resolve(strict=True)
        if not resolved.is_file():
            raise ValueError(f"O favorito não é um arquivo: {resolved}")
        try:
            relative = resolved.relative_to(resolved_root)
        except ValueError as error:
            raise ValueError(
                f"O favorito está fora da pasta de {kind}s: {resolved}"
            ) from error
        entries.append((resolved, relative))
    return entries
