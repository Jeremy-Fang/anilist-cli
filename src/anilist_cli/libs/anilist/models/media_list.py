
from pydantic import BaseModel, validate_call

from .enums import MediaListStatus, MediaType
from .media_list_entry import MediaListEntry


class MediaList(BaseModel):
    user_id: int
    type: MediaType
    status: MediaListStatus
    entries: list[MediaListEntry]

    @validate_call
    def get_media_list_entry(self) -> MediaListEntry:
        raise NotImplementedError()
