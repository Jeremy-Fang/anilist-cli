from .media_title import MediaTitle
from .media_status import MediaStatus
from .media_format import MediaFormat

from pydantic import BaseModel

from abc import ABC


class Media(BaseModel, ABC):
    media_id: int
    title: MediaTitle
    status: MediaStatus
    popularity: int
    average_score: float
    format: MediaFormat
