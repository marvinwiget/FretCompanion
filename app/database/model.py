from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    rec_mbid: Mapped[str | None] = mapped_column(String(36), unique=True)
    track_name: Mapped[str] = mapped_column(String(255))
    artist_name: Mapped[str] = mapped_column(String(255))
    analysis: Mapped[dict] = mapped_column(JSON)