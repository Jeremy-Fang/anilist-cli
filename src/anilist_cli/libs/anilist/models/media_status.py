from enum import Enum


class MediaStatus(Enum):
    FINISHED = 1
    RELEASING = 2
    NOT_YET_RELEASED = 3
    CANCELLED = 4
    HIATUS = 5
