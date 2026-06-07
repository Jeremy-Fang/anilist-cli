from abc import ABC

from pydantic import BaseModel, Field

from .media_title import MediaTitle


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
    media_status: str | None = Field(default=None, alias="status")
    popularity: int | None = Field(default=None)
    average_score: float | None = Field(default=None, alias="averageScore")
    media_format: str | None = Field(default=None, alias="format")
    media_type: str | None = Field(default=None, alias="type")
    episodes: int | None = Field(default=None)
    chapters: int | None = Field(default=None)
    volumes: int | None = Field(default=None)
