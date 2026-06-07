from datetime import date, datetime

from anilist_cli.utils.common import date_to_fuzzydate, fuzzydate_to_date


def test_date_to_fuzzydate_expect_pass():
    now = datetime.now()
    expected = {"year": now.year, "month": now.month, "day": now.day}
    assert expected == date_to_fuzzydate(now.date())


def test_date_to_fuzzydate_expect_fail():
    now = datetime.now()
    wrong = {"year": now.year, "month": now.month + 1, "day": now.day}
    assert wrong != date_to_fuzzydate(now.date())


def test_fuzzydate_to_date_expect_pass():
    now = datetime.now()
    expected = date(now.year, now.month, now.day)
    fuzzydate = {"year": now.year, "month": now.month, "day": now.day}
    assert expected == fuzzydate_to_date(fuzzydate)


def test_fuzzydate_to_date_missing_field_returns_none():
    fuzzydate = {"year": 2024, "day": 15}
    assert fuzzydate_to_date(fuzzydate) is None


def test_fuzzydate_to_date_none_field_returns_none():
    fuzzydate = {"year": 2024, "month": None, "day": 15}
    assert fuzzydate_to_date(fuzzydate) is None
