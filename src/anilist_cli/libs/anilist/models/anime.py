from .enums import *

from .complete_document import CompleteDocument
from .list_entry_changes import ListEntryChanges

from typing import List, Optional, Any

from pydantic import Field, validate_call

from ....utils.common import fuzzydate_to_date


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
        """
        Function that takes a key, value pair of a pending change and
        adds it to the pending changes of a media entry.

        @type key: str
        @type value: Any
        @param key: the attribute of the media entry to update
        @param value: the updated value corresponding to the key
        @rtype: bool
        @returns: whether or not the changes could be added
        """

        if key not in ListEntryChanges.keys():
            return False

        if type(value) != ListEntryChanges.required_type(key):
            return False

        if self.changes == None:
            self.changes = ListEntryChanges()

        self.changes[key] = value

        return True

    @validate_call
    async def update_list_entry(self) -> bool:
        """
        Function that pushes pending changes of this media entry to Anilist

        @rtype: bool
        @returns: whether or not the changes were successfully pushed
        """

        if self.changes == None:
            return False

        data = await self.adapter.update_list_entry(self.media_id, self.changes)

        # update values with response data from anilist api
        for key in data.keys():
            setattr(self, key, data[key])

        self.changes = None

        return True
