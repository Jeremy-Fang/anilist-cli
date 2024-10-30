from .enums import *
from .media_title import MediaTitle

from abc import ABC


class Media(ABC):
    id: int
    title: MediaTitle
    status: MediaStatus
    popularity: int
    average_score: float
    format: MediaFormat
    type: MediaType
