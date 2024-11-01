from .enums import *

from .complete_document import CompleteDocument

from typing import List, Optional

from pydantic import Field, validate_call


class Anime(CompleteDocument):
    """
    Object containing detailed information on an Anime

    Attributes:
    duration: int | None duration of anime episode
    season: MediaSeason
    end_date: date end date of media
    favorites: int number of users who favorited a media
    source: MediaSource source for the media (ex. light novel)
    """

    duration: Optional[int] = Field(default=None)
    season: MediaSeason
    season_year: int = Field(alias="seasonYear")

    @validate_call
    def add_changes(self) -> bool:
        return True

    @validate_call
    def update_media_entry(self) -> bool:
        return True
