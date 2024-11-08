from .enums import *
from .media_title import MediaTitle

from abc import ABC

from typing import Optional

from pydantic import BaseModel, Field


class Media(ABC, BaseModel):
    """
    Interface representing an anilist media entry

    Attributes:
    media_id: int anilist media id
    media_title: MediaTitle title of media entry
    media_status: str | None current releasing status of media entry
    popularity: int number of users who added this media to their lists
    average_score: float | None average score of the media
    media_format: str | None format of the media
    media_type: str | None anime or manga
    episodes: int | None number of episodes in the media
    chapters: int | None number of chapters in the media
    volumes: int | None number of volumes in the media
    """

    media_id: int = Field(alias="id")
    media_title: MediaTitle = Field(alias="title")
    media_status: Optional[str] = Field(default=None, alias="status")
    popularity: int = Field(default=None)
    average_score: Optional[float] = Field(default=None, alias="averageScore")
    media_format: Optional[str] = Field(default=None, alias="format")
    media_type: Optional[str] = Field(default=None, alias="type")
    episodes: Optional[int] = Field(default=None)
    chapters: Optional[int] = Field(default=None)
    volumes: Optional[int] = Field(default=None)
