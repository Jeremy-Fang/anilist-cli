from .enums import *

from .complete_document import CompleteDocument

from .manga import Manga
from .media_preview import MediaPreview

from typing import Optional

from pydantic import validate_call, Field


class MangaPreview(MediaPreview):

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    async def get_info(self) -> None:
        data = await self.api.get_media_info(self.media_id)

        print(data)
