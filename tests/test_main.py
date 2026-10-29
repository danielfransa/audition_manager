from pathlib import Path

from audition_manager.main import packaging_smoke_test


def test_packaging_smoke_test_accepts_bundled_renderer(
    tmp_path: Path, monkeypatch
) -> None:
    renderer = tmp_path / "nam-render.exe"
    renderer.touch()
    monkeypatch.setenv("AUDITION_MANAGER_NAM_RENDERER", str(renderer))

    assert packaging_smoke_test() == 0


def test_packaging_smoke_test_rejects_missing_renderer(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv(
        "AUDITION_MANAGER_NAM_RENDERER", str(tmp_path / "missing-renderer.exe")
    )

    assert packaging_smoke_test() == 1
