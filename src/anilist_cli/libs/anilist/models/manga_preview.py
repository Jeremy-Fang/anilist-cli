from .enums import *

from .complete_document import CompleteDocument

from .manga import Manga
from .media_preview import MediaPreview

from pydantic import validate_call


class MangaPreview(MediaPreview):
    """
    Object containing preview info on a manga
    """
