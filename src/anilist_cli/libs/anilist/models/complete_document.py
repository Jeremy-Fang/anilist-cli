from .enums import *

from .list_entry_interface import ListEntry
from .media_interface import Media

from abc import abstractmethod

from typing import List, Optional

from pydantic import Field

from datetime import date


class CompleteDocument(ListEntry, Media):
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
