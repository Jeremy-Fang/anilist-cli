from pydantic import BaseModel


class MediaTitle(BaseModel):
    english: str | None = None
    romaji: str | None = None
