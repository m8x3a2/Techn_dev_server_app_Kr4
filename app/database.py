# ============================================================
# Настройка подключения к базе данных (SQLite через SQLAlchemy)
# ============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# URL базы данных берётся из переменной окружения,
# по умолчанию используется SQLite файл ./kr4.db
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kr4.db")

# Параметр connect_args нужен только для SQLite (многопоточность)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency для FastAPI — открывает и закрывает сессию БД."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
