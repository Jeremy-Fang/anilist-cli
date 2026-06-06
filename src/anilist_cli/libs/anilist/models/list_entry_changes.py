import types
from datetime import date

from pydantic import BaseModel, Field

from .enums import MediaListStatus


class ListEntryChanges(BaseModel):
    """
    Class representing pending changes to a list entry

    Attributes:
    status: MediaListStatus | None list entry status
    score: Float | None score of media on the list entry
    progress: int | None progress of logged in user in the media
    progress_volumes: int | None progress in volumes for physical media
    repeat: int | None number of rewatches/rereads of media
    note: str | None note about the media
    started_at: date | None date that the media was started
    completed_at: date | None date that the media was completed
    """

    status: MediaListStatus | None = Field(default=None)
    score: float | None = Field(default=None)
    progress: int | None = Field(default=None)
    progress_volumes: int | None = Field(default=None, alias="progressVolumes")
    repeat: int | None = Field(default=None)
    note: str | None = Field(default=None)
    started_at: date | None = Field(default=None, alias="startedAt")
    completed_at: date | None = Field(default=None, alias="completedAt")

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    @staticmethod
    def keys():
        return ListEntryChanges.__dict__["__annotations__"].keys()

    @staticmethod
    def required_type(key: str):
        annotations = ListEntryChanges.__dict__["__annotations__"]
        if key not in annotations:
            return ""
        annotation = annotations[key]
        if isinstance(annotation, types.UnionType):
            for arg in annotation.__args__:
                if arg is not type(None):
                    return arg
        return annotation
