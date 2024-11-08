from .media_interface import Media
from .list_entry_interface import ListEntry

from pydantic import validate_call

from Typing import Any


class MediaListEntry(ListEntry):
    id: int
    media: Media

    @validate_call
    def add_change(self, field: str, value: Any) -> bool:
        self.changes[field] = value

        return True

    @validate_call
    def update_media_entry() -> bool:
        return True
