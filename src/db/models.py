from typing import Annotated

from sqlmodel import Field, SQLModel, Relationship

class Video(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str 
    name: str
    location: str | None
    transcript: str | None
    clips: list["Clip"] = Relationship(back_populates="video")

class Clip(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    start: str
    end: str
    link: str
    video_id: int | None = Field(default=None, foreign_key="video.id", ondelete="SET NULL")
    video: Video | None = Relationship(back_populates="clips")