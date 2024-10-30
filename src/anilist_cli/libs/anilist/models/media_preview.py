from .enums import *

from ..anilist import AnilistAPI
from .media_interface import Media
from .list_entry_interface import ListEntry
from .complete_document import CompleteDocument

from .list_entry_changes import ListEntryChanges
from .media_title import MediaTitle

from abc import abstractmethod


class MediaPreview(ListEntry, Media):

    def __init__(
        self,
        api: AnilistAPI,
        id: int,
        title: MediaTitle,
        status: MediaStatus,
        popularity: int,
        average_score: float,
        format: MediaFormat,
        type: MediaType,
        list_status: MediaListStatus | None = None,
        progress: int | None = None,
        repeat: int | None = None,
        score: float | None = None,
        changes: ListEntryChanges | None = None,
    ):
        self.api = api
        self.id = id
        self.title = title
        self.status = status
        self.popularity = popularity
        self.average_score = average_score
        self.format = format
        self.type = type
        self.list_status = list_status
        self.progress = progress
        self.repeat = repeat
        self.score = score
        self.changes = changes

    @abstractmethod
    def get_info(self) -> CompleteDocument: ...
