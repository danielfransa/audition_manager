"""SQLite persistence for impulse-response metadata."""

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from audition_manager.library.models import ImpulseResponse


class ImpulseResponseRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(database_path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._migrate()

    def _migrate(self) -> None:
        with self._connection:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                )
                """
            )
            version = self._connection.execute(
                "SELECT COALESCE(MAX(version), 0) FROM schema_version"
            ).fetchone()[0]
            if version < 1:
                self._connection.execute(
                    """
                    CREATE TABLE impulse_response (
                        path TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        sample_rate INTEGER NOT NULL CHECK(sample_rate > 0),
                        channels INTEGER NOT NULL CHECK(channels > 0),
                        favorite INTEGER NOT NULL DEFAULT 0 CHECK(favorite IN (0, 1)),
                        rating INTEGER NOT NULL DEFAULT 0 CHECK(rating BETWEEN 0 AND 5),
                        notes TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                self._connection.execute("INSERT INTO schema_version(version) VALUES (1)")

    def upsert_many(self, items: Iterable[ImpulseResponse]) -> None:
        values = [
            (str(item.path.resolve()), item.name, item.sample_rate, item.channels)
            for item in items
        ]
        with self._connection:
            self._connection.executemany(
                """
                INSERT INTO impulse_response(path, name, sample_rate, channels)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    name = excluded.name,
                    sample_rate = excluded.sample_rate,
                    channels = excluded.channels,
                    updated_at = CURRENT_TIMESTAMP
                """,
                values,
            )

    def get(self, path: Path) -> ImpulseResponse | None:
        row = self._connection.execute(
            """
            SELECT path, name, sample_rate, channels, favorite, rating, notes
            FROM impulse_response WHERE path = ?
            """,
            (str(path.resolve()),),
        ).fetchone()
        if row is None:
            return None
        return ImpulseResponse(
            path=Path(row["path"]), name=row["name"],
            sample_rate=row["sample_rate"], channels=row["channels"],
            favorite=bool(row["favorite"]), rating=row["rating"], notes=row["notes"],
        )

    def set_favorite(self, path: Path, favorite: bool) -> None:
        self._update(path, "favorite", int(favorite))

    def set_rating(self, path: Path, rating: int) -> None:
        if not 0 <= rating <= 5:
            raise ValueError("A avaliação deve estar entre 0 e 5.")
        self._update(path, "rating", rating)

    def set_notes(self, path: Path, notes: str) -> None:
        self._update(path, "notes", notes)

    def _update(self, path: Path, column: str, value: object) -> None:
        with self._connection:
            cursor = self._connection.execute(
                f"UPDATE impulse_response SET {column} = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE path = ?",
                (value, str(path.resolve())),
            )
        if cursor.rowcount != 1:
            raise KeyError(f"IR não encontrado na biblioteca: {path}")

    def close(self) -> None:
        self._connection.close()
