from abc import ABC
from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from .list_entry_changes import ListEntryChanges


class ListEntry(ABC, BaseModel):
    """
    Interface similar to a list entry

    Attributes:
    adapter: Any anilist adapter address
    list_entry_status: str | None status of a list entry
    progress: int | None progress of list entry
    repeat: int | None number of repeats of list entry
    score: float | None score of the list entry
    changes: ListEntryChanges | None changes to make to the list entry
    """

    adapter: Any
    list_entry_status: str | None = Field(default=None)
    progress: int | None = Field(default=None)
    repeat: int | None = Field(default=None)
    score: float | None = Field(default=None)
    notes: str | None = Field(default=None)
    started_at: date | None = Field(default=None, alias="startedAt")
    completed_at: date | None = Field(default=None, alias="completedAt")
    changes: ListEntryChanges | None = Field(default=None)
