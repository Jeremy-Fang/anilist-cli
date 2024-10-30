from .enums import *
from .list_entry_changes import ListEntryChanges

from ..anilist import AnilistAPI

from abc import ABC


class ListEntry(ABC):
    api: AnilistAPI
    list_entry: MediaListStatus | None
    progress: int | None
    repeat: int | None
    score: float | None
    changes: ListEntryChanges | None
