from datetime import date
from unittest.mock import MagicMock

import pytest

from anilist_cli.libs.anilist.adapter import AnilistAdapter
from anilist_cli.libs.anilist.models.enums import MediaListStatus


@pytest.fixture
def adapter():
    return AnilistAdapter(api=MagicMock())


# --- __dict_enums_to_strs__ ---

def test_dict_enums_to_strs_converts_single_enum(adapter):
    d = {"status": MediaListStatus.CURRENT}
    adapter.__dict_enums_to_strs__(d)
    assert d == {"status": "CURRENT"}


def test_dict_enums_to_strs_converts_enum_list(adapter):
    d = {"status_in": [MediaListStatus.CURRENT, MediaListStatus.COMPLETED]}
    adapter.__dict_enums_to_strs__(d)
    assert d == {"status_in": ["CURRENT", "COMPLETED"]}


def test_dict_enums_to_strs_leaves_non_enums_unchanged(adapter):
    d = {"progress": 10, "score": 8.5}
    adapter.__dict_enums_to_strs__(d)
    assert d == {"progress": 10, "score": 8.5}


# --- __dict_dates_to_fuzzy__ ---

def test_dict_dates_to_fuzzy_converts_date(adapter):
    d = {"started_at": date(2023, 4, 15)}
    adapter.__dict_dates_to_fuzzy__(d)
    assert d == {"started_at": {"year": 2023, "month": 4, "day": 15}}


def test_dict_dates_to_fuzzy_leaves_non_dates_unchanged(adapter):
    d = {"progress": 10, "score": 8.5}
    adapter.__dict_dates_to_fuzzy__(d)
    assert d == {"progress": 10, "score": 8.5}


# --- __parse_media_list_entry__ ---

def test_parse_media_list_entry_flattens_entry(adapter):
    d = {
        "id": 1,
        "mediaListEntry": {"status": "CURRENT", "progress": 5, "score": 7.5},
    }
    adapter.__parse_media_list_entry__(d)
    assert "mediaListEntry" not in d
    assert d["list_entry_status"] == "CURRENT"
    assert d["progress"] == 5
    assert d["score"] == 7.5


def test_parse_media_list_entry_zero_score_becomes_none(adapter):
    d = {
        "id": 1,
        "mediaListEntry": {"status": "CURRENT", "progress": 5, "score": 0},
    }
    adapter.__parse_media_list_entry__(d)
    assert d["score"] is None


def test_parse_media_list_entry_no_key_leaves_dict_unchanged(adapter):
    d = {"id": 1, "title": "test"}
    adapter.__parse_media_list_entry__(d)
    assert d == {"id": 1, "title": "test"}


def test_parse_media_list_entry_none_value_leaves_dict_unchanged(adapter):
    d = {"id": 1, "mediaListEntry": None}
    adapter.__parse_media_list_entry__(d)
    assert "list_entry_status" not in d


