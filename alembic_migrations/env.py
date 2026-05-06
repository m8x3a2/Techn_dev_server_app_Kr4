# alembic_migrations/env.py
# Точка входа Alembic — настраивает подключение к БД и запускает миграции

import os
import sys
from pathlib import Path
from logging.config import fileConfig

# Добавляем корень проекта в sys.path, чтобы работал импорт "from app.models import Base"
# Это нужно и на Windows, и на Linux при запуске alembic без PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import engine_from_config, pool
from alembic import context


# Импортируем Base и модели, чтобы Alembic знал о схеме
from app.models import Base  # noqa: F401 — нужен для autogenerate

# Конфигурация из alembic.ini
config = context.config

# Настройка логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаём метаданные моделей Alembic для автогенерации миграций
target_metadata = Base.metadata

# Переопределяем URL из переменной окружения (если задана)
db_url = os.getenv("DATABASE_URL", "sqlite:///./kr4.db")
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме (без реального подключения)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # нужно для SQLite ALTER TABLE
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в online-режиме (с реальным подключением)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # нужно для SQLite ALTER TABLE
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
