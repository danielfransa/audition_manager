import json
from pathlib import Path

from audition_manager.config.preferences import PreferencesStore, UserPreferences


def test_missing_and_corrupt_files_return_defaults(tmp_path: Path) -> None:
    store = PreferencesStore(tmp_path / "preferences.json")
    assert store.load() == UserPreferences()
    store.path.write_text("not json", encoding="utf-8")
    assert store.load() == UserPreferences()


def test_preferences_round_trip_and_atomic_write(tmp_path: Path) -> None:
    store = PreferencesStore(tmp_path / "data" / "preferences.json")
    expected = UserPreferences(
        last_di_file=tmp_path / "di.wav",
        last_ir_directory=tmp_path / "irs",
        last_export_directory=tmp_path / "exports",
        output_device_name="Speakers",
        output_host_api="WASAPI",
        output_gain_db=-12,
        loop_enabled=False,
    )
    store.save(expected)
    assert store.load() == expected
    assert json.loads(store.path.read_text(encoding="utf-8"))["version"] == 1
    assert list(store.path.parent.glob("*.tmp")) == []


def test_invalid_values_use_safe_defaults_and_gain_is_clamped(tmp_path: Path) -> None:
    path = tmp_path / "preferences.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "last_di_file": 123,
                "output_device_name": [],
                "output_gain_db": -80,
                "loop_enabled": "yes",
            }
        ),
        encoding="utf-8",
    )
    preferences = PreferencesStore(path).load()
    assert preferences.last_di_file is None
    assert preferences.output_device_name is None
    assert preferences.output_gain_db == -24
    assert preferences.loop_enabled
