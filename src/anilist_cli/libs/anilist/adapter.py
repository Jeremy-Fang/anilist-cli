import re
from datetime import date
from enum import Enum

from pydantic import validate_call

from ...utils.common import date_to_fuzzydate, fuzzydate_to_date
from .client import AnilistClient
from .models.anime import Anime
from .models.anime_preview import AnimePreview
from .models.complete_document import CompleteDocument
from .models.enums import MediaListStatus, MediaType
from .models.filter import MediaFilter, MediaListFilter, PageFilter
from .models.list_entry_changes import ListEntryChanges
from .models.manga import Manga
from .models.manga_preview import MangaPreview
from .models.media_list_entry import MediaListEntry
from .models.media_title import MediaTitle
from .queries import get_expanded_media_info, get_media, get_media_list, update_entry

# regex cleaner to get rid of unwanted html tags
CLEANR = re.compile("<.*?>")


class AnilistAdapter:
    """
    Adapter to turn graphQL response data into usable class instances

    Attributes:
    api: AnilistClient instance of api class
    """

    def __init__(self, api: AnilistClient):
        """
        Initialize the adapter with an AnilistClient instance to wrap
        """
        self.api = api

    def __dict_enums_to_strs__(self, d: dict) -> None:
        """
        Helper function that converts enum values in a dictionary into
        strings
        """

        for key in d.keys():
            if type(d[key]) is list:
                if not d[key]:
                    continue
                if issubclass(type(d[key][0]), Enum):
                    val = []
                    for entry in d[key]:
                        val.append(entry.name)
                    d[key] = val.copy()
            else:
                if issubclass(type(d[key]), Enum):
                    d[key] = d[key].name

        return None

    def __dict_dates_to_fuzzy__(self, d: dict) -> None:
        """
        Helper function that converts datetime.date values in a
        dictionary into fuzzy date objects
        """

        for key in d:
            if type(d[key]) is date:
                d[key] = date_to_fuzzydate(d[key])

        return None

    def __parse_media_list_entry__(self, d: dict) -> None:
        """
        Helper function that flattens a media list entry in a dictionary
        """

        if "mediaListEntry" not in d or d["mediaListEntry"] is None:
            return

        media_list_entry = d["mediaListEntry"]

        d["list_entry_status"] = media_list_entry["status"]
        d["progress"] = media_list_entry["progress"]
        d["score"] = (
            media_list_entry["score"] if media_list_entry["score"] != 0 else None
        )

        del d["mediaListEntry"]

        return None

    def __filter_to_graphql__(
        self,
        query: str,
        filter: MediaFilter | MediaListFilter,
        page_filter: PageFilter | None = None,
    ) -> tuple:
        """
        Builds a (query, variables) tuple from a filter and optional page filter.

        @type query: str
        @type filter: MediaFilter | MediaListFilter
        @type page_filter: PageFilter | None
        @param query: graphQL query string
        @param filter: a type of filter for media
        @param page_filter: page parameters for the query
        @rtype: Tuple
        @returns: tuple of (query string, variables dict)
        """

        variables = filter.model_dump(by_alias=True)
        page_variables = page_filter.model_dump(by_alias=True) if page_filter else {}

        query_variables = {
            key: value for (key, value) in variables.items() if value is not None
        }

        self.__dict_enums_to_strs__(query_variables)
        self.__dict_dates_to_fuzzy__(query_variables)

        if page_filter:
            query_variables.update(page_variables)

        return (query, query_variables)

    @validate_call
    async def search(
        self,
        filters: MediaFilter,
        page_filter: PageFilter = PageFilter(perPage=20),
    ) -> tuple:
        """
        Function that queries anilist API for media filtered by filters

        @type filters: MediaFilter
        @type page_filter: PageFilter
        @param filters: MediaFilter containing media filter key-value pairs
        @param page_filter: PageFilter containing page parameters for the query
        @rtype: Tuple
        @returns: Tuple containing dictionaries representing the top 20 \
        media matching the filters and results info
        """

        data = await self.api.get_data(
            *self.__filter_to_graphql__(get_media, filters, page_filter)
        )

        if data is None:
            return ([], {})

        results_info = data["data"]["Page"]["pageInfo"]
        data = data["data"]["Page"]["media"]

        # cleans data
        for entry in data:
            entry["adapter"] = self
            entry["title"] = MediaTitle(**entry["title"])

            self.__parse_media_list_entry__(entry)

        results = []

        for entry in data:
            if entry["type"] == "ANIME":
                results.append(AnimePreview(**entry))
            else:
                results.append(MangaPreview(**entry))

        return (results, results_info)

    def __changes_to_graphql__(
        self, query: str, media_id: int, changes: ListEntryChanges
    ) -> tuple:
        """
        Builds a (query, variables) tuple from a media id and list entry changes.

        @type query: str
        @type media_id: int
        @type changes: ListEntryChanges
        @param query: graphQL mutation string
        @param media_id: id of media corresponding to list entry to update
        @param changes: pending changes for a list entry
        @rtype: Tuple
        @returns: tuple of (query string, variables dict)
        """

        variables = changes.model_dump(by_alias=True)
        query_variables = {
            key: value for (key, value) in variables.items() if value is not None
        }

        query_variables["mediaId"] = media_id

        self.__dict_enums_to_strs__(query_variables)
        self.__dict_dates_to_fuzzy__(query_variables)

        return (query, query_variables)

    @validate_call
    async def update_list_entry(
        self, media_id: int, changes: ListEntryChanges
    ) -> dict | None:
        """
        Function that applies ListEntryChanges to the media which corresponds to
        the list entry for the logged in user if possible (or creates list entry
        if it does not exist)

        @type media_id: int
        @type changes: ListEntryChanges
        @param media_id: id of media corresponding to list entry to update
        @param changes: Object representing the changes to apply to the list entry
        @rtype: dict | None
        @returns dict with updated entry info, or None if the update failed
        """

        data = await self.api.authenticated_call(
            *self.__changes_to_graphql__(update_entry, media_id, changes)
        )

        if data is None:
            return None

        data = data["data"]["SaveMediaListEntry"]

        data["list_entry_status"] = data["status"]
        data["started_at"] = data["startedAt"]
        data["completed_at"] = data["completedAt"]

        del data["status"]
        del data["startedAt"]
        del data["completedAt"]

        for key in list(data.keys()):
            if type(data[key]) is dict:
                data[key] = fuzzydate_to_date(data[key])
            if data[key] is None:
                del data[key]

        return data

    @validate_call
    async def get_media_info(self, id: int) -> CompleteDocument | None:
        """
        Function that gets detailed information on a media entry matching
        the id

        @type id: int
        @param id: id of media
        @rtype: CompleteDocument
        @returns: document containing detailed information on the matching media
        """

        media_filters = MediaFilter()
        media_filters["media_id"] = id

        data = await self.api.get_data(
            *self.__filter_to_graphql__(get_expanded_media_info, media_filters)
        )

        if data is None:
            return None

        data = data["data"]["Media"]

        data["adapter"] = self
        data["title"] = MediaTitle(**data["title"])
        data["startDate"] = fuzzydate_to_date(data.get("startDate", None))
        data["endDate"] = fuzzydate_to_date(data.get("endDate", None))

        if "description" in data:
            data["description"] = re.sub(CLEANR, "", data["description"])

        for i, genre in enumerate(data["genres"]):
            data["genres"][i] = "_".join(genre.upper().replace("-", " ").split())

        self.__parse_media_list_entry__(data)

        if data["type"] == "ANIME":
            return Anime(**data)
        else:
            return Manga(**data)

    @validate_call
    async def get_media_list(
        self,
        user_name: str,
        media_type: MediaType,
        media_list_status: list[MediaListStatus],
    ) -> list[tuple]:
        """
        Function that requests media lists based on function parameters

        @type user_name: str
        @type media_type: MediaType
        @type media_list_status: List[MediaListStatus]
        @param user_name: anilist username
        @param media_type: anime or manga
        @param media_list_status: list of media statuses
        @rtype: List[Tuple]
        @returns: list of tuples with media list info (length, status, etc.)
        """

        list_filters = MediaListFilter()

        list_filters["user_name"] = user_name
        list_filters["media_type"] = media_type
        list_filters["status_in"] = media_list_status

        data = await self.api.get_data(
            *self.__filter_to_graphql__(get_media_list, list_filters)
        )

        if data is None:
            return []

        data = data["data"]["MediaListCollection"]["lists"]
        results = []

        for media_list in data:
            entries = media_list["entries"]
            entry_objects = []

            for entry in entries:
                entry["adapter"] = self
                entry["title"] = MediaTitle(**entry["media"]["title"])
                del entry["media"]["title"]
                entry["startedAt"] = fuzzydate_to_date(entry["startedAt"])
                entry["completedAt"] = fuzzydate_to_date(entry["completedAt"])

                entry_objects.append(MediaListEntry(**entry))

            results.append(
                (
                    media_list["name"],
                    media_list["status"],
                    len(entries),
                    entry_objects,
                )
            )

        return results
