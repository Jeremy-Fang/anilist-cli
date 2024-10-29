from .media_season import MediaSeason
from .complete_document import CompleteDocument
from .media import Media

from pydantic import BaseModel, validate_call


class Anime(CompleteDocument, Media, BaseModel):
    episodes: int
    season: MediaSeason
    seasonYear: int

    @validate_call
    def add_changes(self) -> bool:
        return True

    @validate_call
    def update_media_entry(self) -> bool:
        return True
