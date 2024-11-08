from .enums import *
from .list_entry_changes import ListEntryChanges

from ..anilist import AnilistAPI

from abc import ABC

from typing import Optional, Any

from pydantic import BaseModel, Field

from datetime import date


class ListEntry(ABC, BaseModel):
    """
    Interface similar to a list entry

    Attributes:
    api: Any anilist api instance
    list_entry_status: str | None status of a list entry
    progress: int | None progress of list entry
    repeat: int | None number of repeats of list entry
    score: float | None score of the list entry
    changes: ListEntryChanges | None changes to make to the list entry
    """

    api: Any
    list_entry_status: Optional[str] = Field(default=None)
    progress: Optional[int] = Field(default=None)
    repeat: Optional[int] = Field(default=None)
    score: Optional[float] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    started_at: Optional[date] = Field(default=None, alias="startedAt")
    completed_at: Optional[date] = Field(default=None, alias="completedAt")
    changes: Optional[ListEntryChanges] = Field(default=None)
