from .enums import *

from typing import List, Optional, Optional

from pydantic import BaseModel, Field


class MediaListFilter(BaseModel):
    user_name: Optional[str] = Field(default=None, alias="userName")
    media_type: Optional[MediaType] = Field(default=None, alias="type")
    status_in: Optional[List[MediaListStatus]] = Field(default=None)
    sort_by: Optional[List[MediaSort]] = Field(default=None)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class PageFilter(BaseModel):
    page: Optional[int] = Field(default=1)
    per_page: Optional[int] = Field(default=50, alias="perPage")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class MediaFilter(BaseModel):
    media_id: Optional[int] = Field(default=None, alias="id")
    season: Optional[MediaSeason] = Field(default=None)
    season_year: Optional[int] = Field(default=None, alias="seasonYear")
    media_type: Optional[MediaType] = Field(default=None, alias="type")
    media_format: Optional[MediaFormat] = Field(default=None, alias="format")
    media_status: Optional[MediaStatus] = Field(default=None, alias="status")
    episodes: Optional[int] = Field(default=None)
    duration: Optional[int] = Field(default=None)
    chapters: Optional[int] = Field(default=None)
    volumes: Optional[int] = Field(default=None)
    on_list: Optional[bool] = Field(default=None, alias="onList")
    average_score: Optional[int] = Field(default=None, alias="averageScore")
    popularity: Optional[int] = Field(default=None)
    search_string: Optional[str] = Field(default=None, alias="search")
    genre_in: Optional[List[str]] = Field(default=None)
    genre_not_in: Optional[List[str]] = Field(default=None)
    tag_in: Optional[List[str]] = Field(default=None)
    tag_not_in: Optional[List[str]] = Field(default=None)
    sort_by: Optional[List[MediaSort]] = Field(default=None, alias="sort")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
