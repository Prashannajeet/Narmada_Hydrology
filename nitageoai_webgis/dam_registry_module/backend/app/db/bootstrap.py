from __future__ import annotations

import os
from pathlib import Path

import psycopg


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql://", 1)
    return url


def bootstrap_database() -> None:
    database_url = normalize_database_url(os.environ["DATABASE_URL"])
    init_dir = Path(os.getenv("DATABASE_INIT_DIR", "/app/database/init"))
    if not init_dir.exists():
        return

    sql_files = [
        init_dir / "001_dam_registry_schema.sql",
        init_dir / "004_field_inspection_module.sql",
        init_dir / "005_risk_register_module.sql",
    ]

    with psycopg.connect(database_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            for sql_file in sql_files:
                if sql_file.exists():
                    cursor.execute(sql_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    bootstrap_database()
