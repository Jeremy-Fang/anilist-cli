from .enums import *

from ..anilist import AnilistAPI
from .complete_document import CompleteDocument

from .anime import Anime
from .media_preview import MediaPreview
from .list_entry_changes import ListEntryChanges

from .media_title import MediaTitle

from pydantic import validate_call


class AnimePreview(MediaPreview):
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
        super().__init__(
            api,
            id,
            title,
            status,
            popularity,
            average_score,
            format,
            type,
            list_status,
            progress,
            repeat,
            score,
            changes,
        )

    @validate_call
    async def get_info(self) -> CompleteDocument:
        data = self.api.get_media_info()

        print(data)
        return super().get_info()
