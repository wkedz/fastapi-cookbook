from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from enum import Enum

class Role(str, Enum):
    basic = "basic"
    premium = "premium"

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        primary_key=True, index=True
    )
    username: Mapped[str] = mapped_column(
        unique=True, index=True
    )
    email: Mapped[str] = mapped_column(
        unique=True, index=True
    )
    hashed_password: Mapped[str]

    role : Mapped[Role] = mapped_column(
        default=Role.basic
    )