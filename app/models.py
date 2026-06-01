from datetime import datetime

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="user", cascade="all, delete-orphan"
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    lat: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    lon: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    weather_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    weather_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="locations")

    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_user_location"),)

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name={self.name}, user_id={self.user_id})>"
