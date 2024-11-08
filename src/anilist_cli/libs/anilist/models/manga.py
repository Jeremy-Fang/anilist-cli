from .enums import *

from .complete_document import CompleteDocument
from .list_entry_changes import ListEntryChanges

from typing import List, Any

from pydantic import Field, validate_call


class Manga(CompleteDocument):
    """
    Object containing detailed information on a Manga
    """

    @validate_call
    def add_changes(self, key: str, value: Any) -> bool:
        return True

    @validate_call
    def update_media_entry(self) -> bool:
        return True
