from .complete_document import CompleteDocument

from .anime import Anime
from .media_preview import MediaPreview

from pydantic import validate_call


class AnimePreview(MediaPreview):
    """
    Object containing preview info on an anime
    """

    @validate_call
    async def get_info(self) -> CompleteDocument:
        """
        Function that returns more detailed information about this anime

        @rtype: CompleteDocument
        @returns: anime media object masked as a CompleteDocument
        """

        data = await self.api.get_media_info(self.media_id)

        return Anime(**data)
