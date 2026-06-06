from datetime import date
from unittest.mock import MagicMock

import pytest

from anilist_cli.libs.anilist.graphql_adapter import GraphQLAdapter
from anilist_cli.libs.anilist.models.enums import MediaListStatus, MediaType


@pytest.fixture
def adapter():
    return GraphQLAdapter(api=MagicMock())


# --- __create_var_type_map__ ---

def test_create_var_type_map_primitive_types(adapter):
    variables = [{"score": 8.5, "progress": 10, "note": "great", "repeat": True}]
    result = adapter.__create_var_type_map__(variables)
    assert result == {"score": "Float", "progress": "Int", "note": "String", "repeat": "Boolean"}


def test_create_var_type_map_enum_value(adapter):
    variables = [{"status": MediaListStatus.CURRENT}]
    result = adapter.__create_var_type_map__(variables)
    assert result == {"status": "MediaListStatus"}


def test_create_var_type_map_list_of_enums(adapter):
    variables = [{"status_in": [MediaListStatus.CURRENT, MediaListStatus.COMPLETED]}]
    result = adapter.__create_var_type_map__(variables)
    assert result == {"status_in": "[MediaListStatus]"}


def test_create_var_type_map_date_value(adapter):
    variables = [{"started_at": date(2023, 1, 1)}]
    result = adapter.__create_var_type_map__(variables)
    assert result == {"started_at": "FuzzyDateInput"}


def test_create_var_type_map_skips_empty_dict(adapter):
    variables = [{}, {"progress": 5}]
    result = adapter.__create_var_type_map__(variables)
    assert result == {"progress": "Int"}


def test_create_var_type_map_merges_multiple_dicts(adapter):
    variables = [{"score": 8.5}, {"progress": 10}]
    result = adapter.__create_var_type_map__(variables)
    assert result == {"score": "Float", "progress": "Int"}


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


# --- __clean_query__ ---

SAMPLE_QUERY = "episodes duration season seasonYear chapters volumes mediaListEntry {{status progress}}"


def test_clean_query_anime_removes_manga_properties(adapter):
    result = adapter.__clean_query__(SAMPLE_QUERY, MediaType.ANIME, True)
    assert "chapters" not in result
    assert "volumes" not in result
    assert "episodes" in result
    assert "season" in result


def test_clean_query_manga_removes_anime_properties(adapter):
    result = adapter.__clean_query__(SAMPLE_QUERY, MediaType.MANGA, True)
    assert "episodes" not in result
    assert "duration" not in result
    assert "season" not in result
    assert "chapters" in result
    assert "volumes" in result


def test_clean_query_removes_media_list_entry_when_logged_out(adapter):
    result = adapter.__clean_query__(SAMPLE_QUERY, MediaType.ANIME, False)
    assert "mediaListEntry" not in result


def test_clean_query_keeps_media_list_entry_when_logged_in(adapter):
    result = adapter.__clean_query__(SAMPLE_QUERY, MediaType.ANIME, True)
    assert "mediaListEntry" in result
