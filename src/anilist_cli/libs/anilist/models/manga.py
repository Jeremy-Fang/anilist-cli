from .media import Media
from .complete_document import CompleteDocument

from pydantic import BaseModel, validate_call


class Manga(CompleteDocument, Media, BaseModel):
    chapters: int

    @validate_call
    def add_changes(self) -> bool:
        return True

    @validate_call
    def update_media_entry(self) -> bool:
        return True
