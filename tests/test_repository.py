from pathlib import Path
import sqlite3

import pytest

from audition_manager.library.models import Capture, ImpulseResponse
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


def test_capture_metadata_survives_rescan_and_reopen(tmp_path: Path) -> None:
    database = tmp_path / "library.sqlite3"
    path = tmp_path / "amp.nam"
    capture = Capture(path, path.name, "0.7.0", "SlimmableContainer", 48000, 2)
    repository = ImpulseResponseRepository(database)
    repository.upsert_captures([capture])
    repository.set_capture_favorite(path, True)
    repository.set_capture_rating(path, 5)
    repository.set_capture_notes(path, "Clean pedal platform")
    repository.upsert_captures([capture])
    repository.close()
    reopened = ImpulseResponseRepository(database)
    item = reopened.get_capture(path)
    assert item is not None
    assert (item.version, item.sample_rate, item.submodel_count) == ("0.7.0", 48000, 2)
    assert (item.favorite, item.rating, item.notes) == (
        True, 5, "Clean pedal platform"
    )
    reopened.close()


def test_existing_version_one_database_migrates_capture_library(tmp_path: Path) -> None:
    database = tmp_path / "library.sqlite3"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY)")
    connection.execute("INSERT INTO schema_version(version) VALUES (1)")
    connection.commit()
    connection.close()
    repository = ImpulseResponseRepository(database)
    path = tmp_path / "amp.nam"
    repository.upsert_captures([
        Capture(path, path.name, "0.7.0", "SlimmableContainer", 48000, 2)
    ])
    assert repository.get_capture(path) is not None
    repository.close()
