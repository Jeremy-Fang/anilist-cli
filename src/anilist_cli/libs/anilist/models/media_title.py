from pydantic import BaseModel, Field

from typing import Optional


class MediaTitle(BaseModel):
    english: Optional[str] = Field(default=None)
    romaji: Optional[str] = Field(default=None)
