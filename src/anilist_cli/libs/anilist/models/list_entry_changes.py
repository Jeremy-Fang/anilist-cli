from .enums import *

from typing import TypedDict, NotRequired


class ListEntryChanges(TypedDict):
    status: NotRequired[MediaListSort]
    score: NotRequired[int]
    progress: NotRequired[int]
    progress_volumes: NotRequired[int]
    repeat: NotRequired[int]
    note: NotRequired[str]
    started_at: NotRequired[str]
    completed_at: NotRequired[str]
