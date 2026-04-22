"""SQLite database helpers for FortZero."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_file: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_file)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_file: Path) -> None:
    db_file.parent.mkdir(parents=True, exist_ok=True)

    schema_path = Path(__file__).resolve().with_name("schema.sql")
    schema_sql = schema_path.read_text(encoding="utf-8")

    with get_connection(db_file) as connection:
        connection.executescript(schema_sql)
        connection.commit()
