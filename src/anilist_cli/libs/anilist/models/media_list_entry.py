from .media import Media
from .list_entry import ListEntry

from .media_list_status import MediaListStatus

from pydantic import BaseModel, validate_call

from Typing import Any


class MediaListEntry(ListEntry, BaseModel):
    id: int
    media: Media

    @validate_call
    def add_change(self, field: str, value: Any) -> bool:
        self.changes[field] = value

        return True

    @validate_call
    def update_media_entry() -> bool:
        return True
