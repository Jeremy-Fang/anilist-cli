from datetime import date


def date_to_fuzzydate(d: date) -> dict:
    """
    Function that serializes a date Object into JSON

    @type d: date
    @param d: datetime.date object
    @rtype: dict
    @returns: dict containing year, month and date attributes
    """

    time = d.isoformat().split("-")

    return {k: int(v) for k, v in zip(["year", "month", "day"], time)}


def fuzzydate_to_date(fuzzy: dict) -> date | None:
    """
    Function that serializes a JSON object into a date Object

    @type fuzzy: dict
    @param fuzzy: JSON fuzzydate
    @rtype: date
    @returns: datetime.date Object represented by fuzzy
    """
    for key in ["year", "month", "day"]:
        if key not in fuzzy or fuzzy[key] is None:
            return None

    return date(fuzzy["year"], fuzzy["month"], fuzzy["day"])
