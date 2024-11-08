from .enums import *

from typing import Optional

import re

from pydoc import locate

from datetime import date

from pydantic import BaseModel, Field


class ListEntryChanges(BaseModel):
    """
    Class representing pending changes to a list entry

    Attributes:
    status: MediaListStatus | None list entry status
    score: Float | None score of media on the list entry
    progress: int | None progress of logged in user in the media
    progress_volumes: int | None progress in volumes for physical media
    repeat: int | None number of rewatches/rereads of media
    note: str | None note about the media
    started_at: date | None date that the media was started
    completed_at: date | None date that the media was completed
    """

    status: Optional[MediaListStatus] = Field(default=None)
    score: Optional[float] = Field(default=None)
    progress: Optional[int] = Field(default=None)
    progress_volumes: Optional[int] = Field(default=None, alias="progressVolumes")
    repeat: Optional[int] = Field(default=None)
    note: Optional[str] = Field(default=None)
    started_at: Optional[date] = Field(default=None, alias="startedAt")
    completed_at: Optional[date] = Field(default=None, alias="completedAt")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    @staticmethod
    def keys():
        return ListEntryChanges.__dict__["__annotations__"].keys()

    @staticmethod
    def required_type(key: str):
        if key not in ListEntryChanges.__dict__["__annotations__"].keys():
            return ""

        type_string = str(ListEntryChanges.__dict__["__annotations__"][key])

        parsed_type = re.search("\[.*\]", type_string).group()[1:-1]

        return locate(parsed_type)
