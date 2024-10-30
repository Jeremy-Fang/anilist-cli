from .enums import *

from .list_entry_interface import ListEntry
from .media_interface import Media

from abc import abstractmethod

from typing import List


class CompleteDocument(ListEntry, Media):
    genres: List[MediaGenre]
    description: str

    @abstractmethod
    def add_changes(self) -> bool: ...

    @abstractmethod
    def update_media_entry(self) -> bool: ...
