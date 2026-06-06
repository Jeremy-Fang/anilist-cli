
from pydantic import BaseModel, Field

from .enums import (
    MediaFormat,
    MediaListStatus,
    MediaSeason,
    MediaSort,
    MediaStatus,
    MediaType,
)


class MediaListFilter(BaseModel):
    user_name: str | None = Field(default=None, alias="userName")
    media_type: MediaType | None = Field(default=None, alias="type")
    status_in: list[MediaListStatus] | None = Field(default=None)
    sort_by: list[MediaSort] | None = Field(default=None)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class PageFilter(BaseModel):
    page: int | None = Field(default=1)
    per_page: int | None = Field(default=50, alias="perPage")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class MediaFilter(BaseModel):
    media_id: int | None = Field(default=None, alias="id")
    season: MediaSeason | None = Field(default=None)
    season_year: int | None = Field(default=None, alias="seasonYear")
    media_type: MediaType | None = Field(default=None, alias="type")
    media_format: MediaFormat | None = Field(default=None, alias="format")
    media_status: MediaStatus | None = Field(default=None, alias="status")
    episodes: int | None = Field(default=None)
    duration: int | None = Field(default=None)
    chapters: int | None = Field(default=None)
    volumes: int | None = Field(default=None)
    on_list: bool | None = Field(default=None, alias="onList")
    average_score: int | None = Field(default=None, alias="averageScore")
    popularity: int | None = Field(default=None)
    search_string: str | None = Field(default=None, alias="search")
    genre_in: list[str] | None = Field(default=None)
    genre_not_in: list[str] | None = Field(default=None)
    tag_in: list[str] | None = Field(default=None)
    tag_not_in: list[str] | None = Field(default=None)
    sort_by: list[MediaSort] | None = Field(default=None, alias="sort")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
