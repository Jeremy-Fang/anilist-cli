class MediaTitle:
    english: str | None
    romaji: str | None

    def __init__(self, english=None, romaji=None) -> None:
        self.english = english
        self.romaji = romaji
