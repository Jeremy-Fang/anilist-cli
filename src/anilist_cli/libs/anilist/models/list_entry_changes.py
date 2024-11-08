from .enums import *

from typing import TypedDict, NotRequired

import re

from pydoc import locate

from datetime import date


class ListEntryChanges(TypedDict):
    status: NotRequired[MediaListStatus]
    score: NotRequired[int]
    progress: NotRequired[int]
    progress_volumes: NotRequired[int]
    repeat: NotRequired[int]
    note: NotRequired[str]
    started_at: NotRequired[date]
    completed_at: NotRequired[date]

    @staticmethod
    def keys():
        return ListEntryChanges.__dict__["__annotations__"].keys()

    @staticmethod
    def required_type(key: str):
        if key not in ListEntryChanges.__dict__["__annotations__"].keys():
            return ""

        type_string = str(ListEntryChanges.__dict__["__annotations__"][key])

        parsed_type = re.search("\[.*\]", type_string).group()[1:-1]

        return locate(parsed_type)
