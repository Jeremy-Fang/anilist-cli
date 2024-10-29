from .media_list_status import MediaListStatus
from .media_list_entry_changes import MediaListEntryChanges

from abc import ABC
from pydantic import BaseModel


class ListEntry(ABC, BaseModel):
    media_entry_status: MediaListStatus | None = None
    progress: int | None = None
    repeat: int | None = None
    score: float | None = None
    changes: MediaListEntryChanges | None = None
