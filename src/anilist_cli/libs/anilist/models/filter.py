from .enums import *

from typing import TypedDict, List, Optional, Union, Optional

from pydantic import BaseModel, Field

media_list_filter_map: dict = {
    "user_name": "userName",
    "media_type": "type",
    "status_in": "status_in",
    "sort_by": "sort",
}

media_filter_map: dict = {
    "media_id": "id",
    "season": "season",
    "season_year": "seasonYear",
    "media_type": "type",
    "media_format": "format",
    "media_status": "status",
    "episodes": "episodes",
    "duration": "duration",
    "chapters": "chapters",
    "volumes": "volumes",
    "on_list": "onList",
    "average_score": "averageScore",
    "popularity": "popularity",
    "search_string": "search",
    "genre_in": "genre_in",
    "genre_not_in": "genre_not_in",
    "tag_in": "tag_in",
    "tag_not_in": "tag_not_in",
    "sort_by": "sort",
}


class MediaListFilter(BaseModel):
    user_name: str = Field(alias="userName")
    media_type: MediaType = Field(alias="type")
    status_in: Optional[List[MediaListStatus]] = Field(default=None)
    sort_by: Optional[List[MediaSort]] = Field(default=None)


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


class Filter(BaseModel):
    graphql_map: dict
    filter: Union[MediaFilter, MediaListFilter]
