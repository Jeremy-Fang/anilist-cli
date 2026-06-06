from datetime import date

from anilist_cli.libs.anilist.models.enums import MediaListStatus
from anilist_cli.libs.anilist.models.list_entry_changes import ListEntryChanges


def test_required_type_int_field():
    assert ListEntryChanges.required_type("progress") is int


def test_required_type_float_field():
    assert ListEntryChanges.required_type("score") is float


def test_required_type_str_field():
    assert ListEntryChanges.required_type("note") is str


def test_required_type_enum_field():
    assert ListEntryChanges.required_type("status") is MediaListStatus


def test_required_type_date_field():
    assert ListEntryChanges.required_type("started_at") is date
    assert ListEntryChanges.required_type("completed_at") is date


def test_required_type_unknown_key_returns_empty_string():
    assert ListEntryChanges.required_type("nonexistent") == ""


def test_keys_contains_all_fields():
    keys = set(ListEntryChanges.keys())
    assert keys == {"status", "score", "progress", "progress_volumes", "repeat", "note", "started_at", "completed_at"}
