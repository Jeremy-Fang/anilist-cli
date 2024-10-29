from .media_type import MediaType
from .media_list_status import MediaListStatus
from .media_list_entry import MediaListEntry

from typing import List

from pydantic import BaseModel, validate_call


class MediaList(BaseModel):
    user_id: int
    type: MediaType
    status: MediaListStatus
    entries: List[MediaListEntry]

    @validate_call
    def get_media_list_entry() -> MediaListEntry:
        return True
