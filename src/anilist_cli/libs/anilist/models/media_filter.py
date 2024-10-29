from .media_season import MediaSeason
from .media_type import MediaType
from .media_format import MediaFormat
from .media_status import MediaStatus
from .media_sort import MediaSort

from typing import TypedDict, List, NotRequired

media_filter_map: dict = {
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


class MediaFilter(TypedDict):
    season: NotRequired[MediaSeason]
    season_year: NotRequired[int]
    media_type: NotRequired[MediaType]
    media_format: NotRequired[MediaFormat]
    media_status: NotRequired[MediaStatus]
    episodes: NotRequired[int]
    duration: NotRequired[int]
    chapters: NotRequired[int]
    volumes: NotRequired[int]
    on_list: NotRequired[bool]
    average_score: NotRequired[int]
    popularity: NotRequired[int]
    search_string: NotRequired[str]
    genre_in: NotRequired[List[str]]
    genre_not_in: NotRequired[List[str]]
    tag_in: NotRequired[List[str]]
    tag_not_in: NotRequired[List[str]]
    sort_by: NotRequired[List[MediaSort]]
