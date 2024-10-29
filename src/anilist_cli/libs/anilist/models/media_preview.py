from .list_entry import ListEntry
from .media import Media
from .complete_document import CompleteDocument

from .media_genre import MediaGenre

from pydantic import BaseModel, validate_call


class MediaPreview(ListEntry, Media, BaseModel):
    @validate_call
    def get_info(self) -> CompleteDocument:
        return CompleteDocument(
            genres=[MediaGenre.ACTION], description="this is a temp description"
        )
