from .complete_document import CompleteDocument

from .anime import Anime
from .media_preview import MediaPreview

from pydantic import validate_call


class AnimePreview(MediaPreview):
    """
    Object containing preview info on an anime
    """
