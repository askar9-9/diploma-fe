from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.app.config import DATABASE_URL


def _ensure_sqlite_dir(database_url: str) -> None:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return

    raw_path = database_url[len(prefix):]
    if raw_path in {":memory:", ""}:
        return

    path = Path(raw_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)


_ensure_sqlite_dir(DATABASE_URL)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
