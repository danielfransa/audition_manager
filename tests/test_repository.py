from pathlib import Path

import pytest

from audition_manager.library.models import ImpulseResponse
from audition_manager.library.repository import ImpulseResponseRepository


def impulse(path: Path, rate: int = 48000, channels: int = 1) -> ImpulseResponse:
    return ImpulseResponse(path, path.name, rate, channels)


def test_migration_upsert_and_metadata_survive_reopen(tmp_path: Path) -> None:
    database = tmp_path / "nested" / "library.sqlite3"
    path = tmp_path / "cab.wav"
    repository = ImpulseResponseRepository(database)
    repository.upsert_many([impulse(path)])
    repository.set_favorite(path, True)
    repository.set_rating(path, 4)
    repository.set_notes(path, "Bright cabinet; good with neck pickup")
    repository.close()

    reopened = ImpulseResponseRepository(database)
    item = reopened.get(path)
    assert item is not None
    assert item.favorite
    assert item.rating == 4
    assert item.notes == "Bright cabinet; good with neck pickup"
    assert item.sample_rate == 48000
    reopened.close()


def test_rescan_updates_audio_metadata_without_losing_user_fields(tmp_path: Path) -> None:
    path = tmp_path / "cab.wav"
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    repository.upsert_many([impulse(path)])
    repository.set_favorite(path, True)
    repository.set_rating(path, 5)
    repository.set_notes(path, "Keep this note")
    repository.upsert_many([impulse(path, rate=44100, channels=2)])
    item = repository.get(path)
    assert item is not None
    assert (item.sample_rate, item.channels) == (44100, 2)
    assert (item.favorite, item.rating) == (True, 5)
    assert item.notes == "Keep this note"
    repository.close()


def test_rating_validation_and_unknown_path(tmp_path: Path) -> None:
    repository = ImpulseResponseRepository(tmp_path / "library.sqlite3")
    with pytest.raises(ValueError):
        repository.set_rating(tmp_path / "missing.wav", 6)
    with pytest.raises(KeyError):
        repository.set_favorite(tmp_path / "missing.wav", True)
    repository.close()
