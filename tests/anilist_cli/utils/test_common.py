from datetime import date, datetime
from anilist_cli.utils.common import *


def test_date_to_fuzzydate_expect_pass():
    now = datetime.now()
    json_object = {"year": now.year, "month": now.month, "day": now.day}

    assert json_object == date_to_fuzzydate(now.date())


def test_date_to_fuzzydate_expect_fail():
    now = datetime.now()
    json_object = {"year": now.year, "month": now.month + 1, "day": now.day}

    assert json_object != date_to_fuzzydate(now.date())


def test_fuzzydate_to_date_expect_pass():
    now = datetime.now()
    expected_date = date(now.year, now.month, now.day)
    fuzzydate = {"year": now.year, "month": now.month, "day": now.day}

    assert expected_date == fuzzydate_to_date(fuzzydate)


def test_fuzzydate_to_date_expect_fail():
    now = datetime.now()
    fuzzydate = {"year": now.year, "day": now.day}

    assert fuzzydate_to_date(fuzzydate) == None
