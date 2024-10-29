from .media_season import MediaSeason
from .media_type import MediaType
from .media_format import MediaFormat
from .media_status import MediaStatus
from .media_sort import MediaSort

from typing import TypedDict, Optional, List


class MediaFilter(TypedDict):
    season: Optional[MediaSeason]
    season_year: Optional[int]
    media_type: Optional[MediaType]
    media_format: Optional[MediaFormat]
    media_status: Optional[MediaStatus]
    episodes: Optional[int]
    duration: Optional[int]
    chapters: Optional[int]
    volumes: Optional[int]
    on_list: Optional[bool]
    average_score: Optional[int]
    popularity: Optional[int]
    search: Optional[str]
    genre_in: Optional[List[str]]
    genre_not_in: Optional[List[str]]
    tag_in: Optional[List[str]]
    tag_not_in: Optional[List[str]]
    sort: Optional[List[MediaSort]]
