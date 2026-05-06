# ============================================================
# ЗАДАНИЕ 9.1 — Модель данных SQLAlchemy для сущности Product
# ============================================================

from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Product(Base):
    """
    Модель товара.
    Поля id, title, price, count добавлены в первой миграции.
    Поле description добавлено во второй миграции (NOT NULL).
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    count = Column(Integer, nullable=False, default=0)
    # Поле description добавлено второй миграцией (NOT NULL со значением по умолчанию)
    description = Column(Text, nullable=False, server_default="")
