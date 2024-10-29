from enum import Enum


class MediaListStatus(Enum):
    CURRENT = 1
    PLANNING = 2
    COMPLETED = 3
    DROPPED = 4
    PAUSED = 5
    REPEATING = 6
