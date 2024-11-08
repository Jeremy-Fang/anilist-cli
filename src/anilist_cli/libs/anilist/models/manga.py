from .enums import *

from .complete_document import CompleteDocument
from .list_entry_changes import ListEntryChanges

from typing import List, Any

from pydantic import Field, validate_call


class Manga(CompleteDocument):
    """
    Object containing detailed information on a Manga
    """

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
    async def update_media_entry(self) -> bool:
        """
        Function that pushes pending changes of this media entry to Anilist

        @rtype: bool
        @returns: whether or not the changes were successfully pushed
        """

        if self.changes == None:
            return False

        data = await self.api.update_media(self.media_id, self.changes)

        print(data)

        return True
