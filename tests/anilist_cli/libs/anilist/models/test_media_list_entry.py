from datetime import date
from unittest.mock import MagicMock

import pytest

from anilist_cli.libs.anilist.models.media_list_entry import MediaListEntry
from anilist_cli.libs.anilist.models.media_title import MediaTitle


def _make_entry(**overrides) -> dict:
    """Replicates the dict state adapter.get_media_list produces before MediaListEntry(**entry)."""
    base = {
        "id": 1,
        "mediaId": 123,
        "media": {},  # leftover after del entry["media"]["title"]
        "adapter": MagicMock(),
        "title": MediaTitle(english="Re:Zero", romaji="Re:Zero"),
        "startedAt": date(2023, 1, 1),
        "completedAt": None,
        "score": 8.5,
        "repeat": 0,
        "progress": 10,
        "notes": "great",
    }
    base.update(overrides)
    return base


def test_media_id_is_populated_from_alias():
    entry = MediaListEntry(**_make_entry())
    assert entry.media_id == 123


def test_leftover_media_key_is_ignored():
    # Pydantic v2 silently drops extra fields (extra='ignore' by default).
    # This confirms the adapter's del entry["media"]["title"] pattern is safe.
    entry = MediaListEntry(**_make_entry(media={"unexpected": "data"}))
    assert entry.media_id == 123
    assert not hasattr(entry, "media")


def test_list_entry_fields_are_set():
    entry = MediaListEntry(**_make_entry())
    assert entry.id == 1
    assert entry.progress == 10
    assert entry.score == 8.5
    assert entry.notes == "great"
    assert entry.started_at == date(2023, 1, 1)
    assert entry.completed_at is None
