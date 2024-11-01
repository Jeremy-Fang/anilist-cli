from .enums import *

from .complete_document import CompleteDocument

from .anime import Anime
from .media_preview import MediaPreview

from pydantic import validate_call


class AnimePreview(MediaPreview):
    """
    Object containing preview info on an anime
    """

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    @validate_call
    async def get_info(self) -> CompleteDocument:
        """
        Function that returns more detailed information about this anime

        @rtype: CompleteDocument
        @returns: anime media object masked as a CompleteDocument
        """
        data = await self.api.get_media_info(self.media_id)

        return Anime(**data)
