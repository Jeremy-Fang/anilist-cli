from .enums import *

from .media_interface import Media
from .list_entry_interface import ListEntry

from .complete_document import CompleteDocument

from abc import abstractmethod


class MediaPreview(ListEntry, Media):
    """
    Interface containing one abstract function to obtain more
    detailed info on the media
    """

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    @abstractmethod
    def get_info(self) -> CompleteDocument: ...
