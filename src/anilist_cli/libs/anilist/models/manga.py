from .enums import *

from .complete_document import CompleteDocument

from typing import List

from pydantic import Field, validate_call


class Manga(CompleteDocument):
    """
    Object containing detailed information on a Manga
    """

    @validate_call
    def add_changes(self) -> bool:
        return True

    @validate_call
    def update_media_entry(self) -> bool:
        return True
