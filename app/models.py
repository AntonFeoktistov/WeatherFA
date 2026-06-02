from datetime import datetime, timezone

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
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(200), nullable=True)
    lat: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    lon: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    weather_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    weather_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="locations")

    __table_args__ = (UniqueConstraint("user_id", "name_en", name="uq_user_location"),)

    def __repr__(self) -> str:
        return f"<Location(id={self.id}, name={self.name_en}, user_id={self.user_id})>"
