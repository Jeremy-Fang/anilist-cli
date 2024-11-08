from .enums import *

from .complete_document import CompleteDocument

from .manga import Manga
from .media_preview import MediaPreview

from pydantic import validate_call


class MangaPreview(MediaPreview):
    """
    Object containing preview info on a manga
    """

    @validate_call
    async def get_info(self) -> CompleteDocument:
        """
        Function that returns more detailed information about this manga

        @rtype: CompleteDocument
        @returns: manga media object masked as a CompleteDocument
        """
        data = await self.api.get_media_info(self.media_id)

        return Manga(**data)
