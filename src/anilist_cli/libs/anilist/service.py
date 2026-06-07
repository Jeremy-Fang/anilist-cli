from .adapter import AnilistAdapter
from .models.complete_document import CompleteDocument
from .models.enums import MediaListStatus, MediaSort, MediaStatus, MediaType
from .models.filter import MediaFilter, PageFilter
from .models.list_entry_changes import ListEntryChanges
from .models.media_preview import MediaPreview


class AnilistService:
    """
    Service layer providing business-level operations over AnilistAdapter.

    Attributes:
    _adapter: AnilistAdapter instance
    """

    def __init__(self, adapter: AnilistAdapter) -> None:
        self._adapter = adapter

    # --- delegation ---

    async def search(
        self,
        filters: MediaFilter,
        page_filter: PageFilter = PageFilter(perPage=20),
    ) -> tuple:
        return await self._adapter.search(filters, page_filter)

    async def get_media_info(self, id: int) -> CompleteDocument | None:
        return await self._adapter.get_media_info(id)

    async def get_media_list(
        self,
        user_name: str,
        media_type: MediaType,
        media_list_status: list[MediaListStatus],
    ) -> list[tuple]:
        return await self._adapter.get_media_list(
            user_name, media_type, media_list_status
        )

    async def update_list_entry(
        self, media_id: int, changes: ListEntryChanges
    ) -> dict | None:
        return await self._adapter.update_list_entry(media_id, changes)

    # --- presets ---

    async def get_trending_media(self, media_type: MediaType) -> list[MediaPreview]:
        """Gets top 20 trending media."""
        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.TRENDING_DESC]
        return (await self._adapter.search(media_filters))[0]

    async def get_all_time_media(self, media_type: MediaType) -> list[MediaPreview]:
        """Gets top 50 all-time popular media."""
        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.POPULARITY_DESC]
        return (await self._adapter.search(media_filters))[0]

    async def get_seasonal_media(self, media_type: MediaType) -> list[MediaPreview]:
        """Gets top 50 currently releasing media."""
        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.TRENDING_DESC]
        media_filters["media_status"] = MediaStatus.RELEASING
        return (await self._adapter.search(media_filters))[0]

    async def get_upcoming_media(self, media_type: MediaType) -> list[MediaPreview]:
        """Gets top 50 not yet released media."""
        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.POPULARITY_DESC]
        media_filters["media_status"] = MediaStatus.NOT_YET_RELEASED
        return (await self._adapter.search(media_filters))[0]
