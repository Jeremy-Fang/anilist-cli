from abc import abstractmethod
from datetime import date
from typing import Any

from pydantic import Field

from .list_entry_interface import ListEntry
from .media_interface import Media


class CompleteDocument(ListEntry, Media):
    """
    Interface for objects that are like detailed media entries

    Attributes:
    genres: List of MediaGenre strs
    description: str description of a media entry
    start_date: date | None start date of media
    end_date: date | None end date of media
    favorites: int number of users who favorited a media
    source: str | None source for the media (ex. light novel)
    """

    genres: list[str]
    description: str
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    favorites: int = Field(alias="favourites")
    source: str | None

    @abstractmethod
    def add_changes(self, key: str, value: Any) -> bool: ...

    @abstractmethod
    def update_list_entry(self) -> bool: ...
