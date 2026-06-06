
from pydantic import BaseModel, Field


class MediaTitle(BaseModel):
    english: str | None = Field(default=None)
    romaji: str | None = Field(default=None)
