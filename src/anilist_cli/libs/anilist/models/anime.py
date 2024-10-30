from .enums import *

from ..anilist import AnilistAPI
from .list_entry_changes import ListEntryChanges
from .media_title import MediaTitle
from .complete_document import CompleteDocument

from typing import List

from pydantic import validate_call


class Anime(CompleteDocument):
    episodes: int
    season: MediaSeason
    season_year: int

    def __init__(
        self,
        api: AnilistAPI,
        id: int,
        title: MediaTitle,
        status: MediaStatus,
        popularity: int,
        average_score: float,
        format: MediaFormat,
        type: MediaType,
        genres: List[MediaGenre],
        description: str,
        episodes: int,
        season: MediaSeason,
        season_year: int,
        list_status: MediaListStatus | None = None,
        progress: int | None = None,
        repeat: int | None = None,
        score: float | None = None,
        changes: ListEntryChanges | None = None,
    ):
        self.api = api
        self.id = id
        self.title = title
        self.status = status
        self.popularity = popularity
        self.average_score = average_score
        self.format = format
        self.type = type
        self.genres = genres
        self.description = description
        self.episodes = episodes
        self.season = season
        self.season_year = season_year
        self.list_status = list_status
        self.progress = progress
        self.repeat = repeat
        self.score = score
        self.changes = changes

    @validate_call
    def add_changes(self) -> bool:
        return True

    @validate_call
    def update_media_entry(self) -> bool:
        return True
