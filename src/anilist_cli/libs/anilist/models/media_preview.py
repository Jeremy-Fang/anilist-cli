from .enums import *

from ..anilist import AnilistAPI
from .media_interface import Media
from .list_entry_interface import ListEntry
from .complete_document import CompleteDocument

from abc import abstractmethod


class MediaPreview(ListEntry, Media):

    @abstractmethod
    def get_info(self) -> CompleteDocument: ...

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)
