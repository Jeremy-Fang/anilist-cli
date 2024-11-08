from .enums import *

from .complete_document import CompleteDocument
from .list_entry_changes import ListEntryChanges

from typing import List, Optional, Any

from pydantic import Field, validate_call


class Anime(CompleteDocument):
    """
    Object containing detailed information on an Anime

    Attributes:
    duration: int | None duration of anime episode
    season: str | None season that the media aired in
    season_year: int | None year which the media will air
    """

    duration: Optional[int] = Field(default=None)
    season: Optional[str] = Field(default=None)
    season_year: Optional[int] = Field(alias="seasonYear")

    @validate_call
    def add_changes(self, key: str, value: Any) -> bool:
        if key not in ListEntryChanges.keys():
            return False

        if type(value) != ListEntryChanges.required_type(key):
            return False

        if self.changes == None:
            self.changes = ListEntryChanges()

        self.changes[key] = value

        return True

    @validate_call
    def update_media_entry(self) -> bool:
        return True
