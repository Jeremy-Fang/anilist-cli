from .enums import *

from .list_entry_interface import ListEntry
from .media_interface import Media

from abc import abstractmethod, ABC

from typing import List, Optional

from pydantic import Field

from datetime import date


class CompleteDocument(ListEntry, Media):
    """
    Interface for objects that are like detailed media entries

    Attributes:
    genres: List of MediaGenre Enums
    description: str description of a media entry
    start_date: date start date of media
    end_date: date end date of media
    favorites: int number of users who favorited a media
    source: MediaSource source for the media (ex. light novel)
    """

    genres: List[MediaGenre]
    description: str
    start_date: Optional[date] = Field(default=None, alias="startDate")
    end_date: Optional[date] = Field(default=None, alias="endDate")
    favorites: int = Field(alias="favourites")
    source: MediaSource

    @abstractmethod
    def add_changes(self) -> bool: ...

    @abstractmethod
    def update_media_entry(self) -> bool: ...
