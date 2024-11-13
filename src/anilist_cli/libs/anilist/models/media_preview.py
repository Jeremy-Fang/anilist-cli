from .media_interface import Media
from .list_entry_interface import ListEntry

from .complete_document import CompleteDocument

from pydantic import validate_call


class MediaPreview(ListEntry, Media):
    """
    Object representing a media pewview containing one function to obtain
    detailed info on the media
    """

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    @validate_call
    async def get_info(self) -> CompleteDocument:
        """
        Function that returns more detailed information about this media

        @rtype: CompleteDocument
        @returns: anime or manga media object masked as a CompleteDocument
        """

        return await self.adapter.get_media_info(self.media_id)
