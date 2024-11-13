from .media_title import MediaTitle

from .list_entry_interface import ListEntry
from .list_entry_changes import ListEntryChanges

from pydantic import validate_call

from typing import Any


class MediaListEntry(ListEntry):
    id: int
    title: MediaTitle

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
