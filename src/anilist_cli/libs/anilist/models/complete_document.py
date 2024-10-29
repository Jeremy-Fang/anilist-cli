from .media_genre import MediaGenre
from .list_entry import ListEntry

from abc import abstractmethod

from typing import List
from pydantic import BaseModel


class CompleteDocument(ListEntry, BaseModel):
    genres: List[MediaGenre]
    description: str

    @abstractmethod
    def add_changes(self) -> bool:
        pass

    @abstractmethod
    def update_media_entry(self) -> bool:
        pass
