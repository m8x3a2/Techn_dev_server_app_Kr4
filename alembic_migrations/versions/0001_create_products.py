"""create products table

Revision ID: 0001_create_products
Revises: 
Create Date: 2025-01-01 00:00:00.000000

ЗАДАНИЕ 9.1 — Шаг 4-5:
Первая миграция создаёт таблицу products с полями id, title, price, count.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# ---- Идентификаторы ревизии ----
revision: str = "0001_create_products"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Создаём таблицу products.
    Поля: id (PK), title (строка), price (вещественное), count (целое).
    """
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_id", "products", ["id"], unique=False)

    # ---- ЗАДАНИЕ 9.1 Шаг 5: добавляем две записи в таблицу ----
    op.execute(
        "INSERT INTO products (title, price, count) VALUES ('Ноутбук', 79999.99, 10)"
    )
    op.execute(
        "INSERT INTO products (title, price, count) VALUES ('Смартфон', 39999.50, 25)"
    )


def downgrade() -> None:
    """Откатываем: удаляем индекс и таблицу."""
    op.drop_index("ix_products_id", table_name="products")
    op.drop_table("products")
