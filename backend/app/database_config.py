from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import sessionmaker

DATABASE_PATH = (Path(__file__).resolve().parents[1] / "data" / "speakspark.db").resolve()
DATABASE_URL = URL.create("sqlite", database=str(DATABASE_PATH))


def create_sqlite_engine(database_path: Path) -> Engine:
    resolved_path = database_path.expanduser().resolve()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = URL.create("sqlite", database=str(resolved_path))
    return create_engine(database_url, connect_args={"check_same_thread": False})


engine = create_sqlite_engine(DATABASE_PATH)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
