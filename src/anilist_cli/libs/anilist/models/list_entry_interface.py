from .enums import *
from .list_entry_changes import ListEntryChanges

from ..anilist import AnilistAPI

from abc import ABC

from typing import Optional, Any

from pydantic import BaseModel, Field


class ListEntry(ABC, BaseModel):
    api: Any
    list_entry_status: Optional[MediaListStatus] = Field(default=None)
    progress: Optional[int] = Field(default=None)
    repeat: Optional[int] = Field(default=None)
    score: Optional[float] = Field(default=None)
    changes: Optional[ListEntryChanges] = Field(default=None)
