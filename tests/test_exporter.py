from pathlib import Path

import pytest

from audition_manager.library.exporter import (
    export_files, export_library_favorites, validate_folder_name,
)


def test_exports_files_preserving_relative_directories_and_metadata(tmp_path: Path) -> None:
    source = tmp_path / "library"
    destination = tmp_path / "exports"
    nested = source / "Mesa"
    nested.mkdir(parents=True)
    destination.mkdir()
    first = nested / "V30.wav"
    second = source / "Greenback.wav"
    first.write_bytes(b"first impulse")
    second.write_bytes(b"second impulse")

    result = export_files(source, [first, second], destination, "Pedal Favorites")

    assert result.directory == destination / "Pedal Favorites"
    assert result.file_count == 2
    assert result.total_bytes == len(b"first impulse") + len(b"second impulse")
    assert (result.directory / "Mesa" / "V30.wav").read_bytes() == b"first impulse"
    assert (result.directory / "Greenback.wav").read_bytes() == b"second impulse"
    assert list(destination.glob(".audition-manager-export-*")) == []


@pytest.mark.parametrize(
    "name", [
        "", " ", ".", "..", " favorites", "favorites ", "a/b", "bad?name",
        "bad.", "CON", "com1.files",
    ]
)
def test_rejects_invalid_cross_platform_folder_names(name: str) -> None:
    with pytest.raises(ValueError):
        validate_folder_name(name)


def test_refuses_existing_destination_without_changing_it(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    favorite = source / "cab.wav"
    favorite.write_bytes(b"audio")
    target = tmp_path / "Favorites"
    target.mkdir()
    marker = target / "keep.txt"
    marker.write_text("untouched")
    with pytest.raises(FileExistsError):
        export_files(source, [favorite], tmp_path, "Favorites")
    assert marker.read_text() == "untouched"


def test_refuses_files_outside_source_root_and_empty_exports(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    outside = tmp_path / "outside.wav"
    outside.write_bytes(b"audio")
    with pytest.raises(ValueError, match="Nenhum IR favorito"):
        export_files(root, [], tmp_path, "Empty")
    with pytest.raises(ValueError, match="fora da pasta"):
        export_files(root, [outside], tmp_path, "Outside")
    assert not (tmp_path / "Empty").exists()
    assert not (tmp_path / "Outside").exists()


def test_refuses_destination_inside_scanned_library(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    favorite = root / "cab.wav"
    favorite.write_bytes(b"audio")
    with pytest.raises(ValueError, match="fora da pasta de IRs"):
        export_files(root, [favorite], root, "Favorites")
    assert not (root / "Favorites").exists()


def test_exports_ir_and_capture_favorites_into_separate_directories(
    tmp_path: Path,
) -> None:
    ir_root = tmp_path / "irs"
    capture_root = tmp_path / "captures"
    destination = tmp_path / "exports"
    (ir_root / "Mesa").mkdir(parents=True)
    (capture_root / "Fender").mkdir(parents=True)
    destination.mkdir()
    ir = ir_root / "Mesa" / "V30.wav"
    capture = capture_root / "Fender" / "Clean.nam"
    ir.write_bytes(b"impulse")
    capture.write_bytes(b"capture")
    result = export_library_favorites(
        destination, "Favoritos",
        ir_root=ir_root, ir_sources=[ir],
        capture_root=capture_root, capture_sources=[capture],
    )
    assert (result.directory / "IRs" / "Mesa" / "V30.wav").read_bytes() == b"impulse"
    assert (result.directory / "Capturas" / "Fender" / "Clean.nam").read_bytes() == b"capture"
    assert (result.ir_count, result.capture_count, result.file_count) == (1, 1, 2)


def test_combined_export_keeps_both_category_directories_when_one_is_empty(
    tmp_path: Path,
) -> None:
    capture_root = tmp_path / "captures"
    destination = tmp_path / "exports"
    capture_root.mkdir()
    destination.mkdir()
    capture = capture_root / "Amp.nam"
    capture.write_bytes(b"capture")
    result = export_library_favorites(
        destination, "Favoritos",
        capture_root=capture_root, capture_sources=[capture],
    )
    assert (result.directory / "IRs").is_dir()
    assert (result.directory / "Capturas" / "Amp.nam").exists()
