"""add description to products

Revision ID: 0002_add_description
Revises: 0001_create_products
Create Date: 2025-01-02 00:00:00.000000

ЗАДАНИЕ 9.1 — Шаги 6-8:
Вторая миграция добавляет поле description (NOT NULL) к таблице products.
Для SQLite используем batch_alter_table (render_as_batch=True в env.py).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# ---- Идентификаторы ревизии ----
revision: str = "0002_add_description"
down_revision: Union[str, None] = "0001_create_products"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Добавляем колонку description (NOT NULL).
    server_default="" позволяет применить миграцию
    к существующим строкам без ошибки NOT NULL.
    """
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(
            sa.Column(
                "description",
                sa.Text(),
                nullable=False,
                server_default="",   # значение по умолчанию для существующих строк
            )
        )


def downgrade() -> None:
    """Откатываем: удаляем колонку description."""
    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_column("description")
