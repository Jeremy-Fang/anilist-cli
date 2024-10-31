from .enums import *
from .media_title import MediaTitle

from abc import ABC

from typing import Optional

from pydantic import BaseModel, Field


class Media(ABC, BaseModel):
    media_id: int = Field(alias="id")
    media_title: MediaTitle = Field(alias="title")
    media_status: MediaStatus = Field(alias="status")
    popularity: int
    average_score: Optional[float] = Field(default=None, alias="averageScore")
    media_format: MediaFormat = Field(alias="format")
    media_type: MediaType = Field(alias="type")
    episodes: Optional[int] = Field(default=None)
    chapters: Optional[int] = Field(default=None)
    volumes: Optional[int] = Field(default=None)
