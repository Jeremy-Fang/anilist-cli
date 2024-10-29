from .media_list_status import MediaListStatus

from pydantic import BaseModel


class MediaListEntryChanges(BaseModel):
    status: MediaListStatus | None = None
    score: int | None = None
    progress: int | None = None
    repeat: int | None = None
