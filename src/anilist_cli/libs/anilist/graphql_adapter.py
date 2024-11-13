from .anilist import AnilistAPI

from ...utils.common import date_to_fuzzydate, fuzzydate_to_date

from enum import Enum

from .models.filter import *
from .models.enums import *
from .models.media_title import MediaTitle

from .models.media_preview import MediaPreview
from .models.anime_preview import AnimePreview
from .models.manga_preview import MangaPreview
from .models.anime import Anime
from .models.manga import Manga

from .models.complete_document import CompleteDocument
from .models.list_entry_changes import ListEntryChanges

from .models.media_list_entry import MediaListEntry

from typing import List, Tuple, Union

from datetime import date

from .queries import *

from collections import deque
import re

from pydantic import validate_call

basic_type_map = {"str": "String", "int": "Int", "float": "Float", "bool": "Boolean"}

# regex cleaner to get rid of unwanted html tags
CLEANR = re.compile("<.*?>")


class GraphQLAdapter:
    """
    Adapter to turn graphQL response data into usable class instances

    Attributes:
    api: AnilistAPI instance of api class
    """

    def __init__(self, api: AnilistAPI):
        """
        Initialize the adapter with an AnilistAPI instance to wrap
        """
        self.api = api

    def __create_var_type_map__(self, variables: dict) -> dict:
        """
        Helper function that creates a map of variable names to their types
        (ex. for the key-value pair "score": 80.4, the entry "score": "Float" is made
        in the result)
        """
        res = {}

        for key in variables.keys():
            if type(variables[key]) is list:
                if issubclass(type(variables[key][0]), Enum):
                    res[key] = "[" + type(variables[key][0]).__name__ + "]"
                else:
                    res[key] = (
                        "[" + basic_type_map[type(variables[key][0]).__name__] + "]"
                    )
            else:
                if issubclass(type(variables[key]), Enum):
                    res[key] = type(variables[key]).__name__
                elif type(variables[key]) is date:
                    res[key] = "FuzzyDateInput"
                else:
                    res[key] = basic_type_map[type(variables[key]).__name__]

        return res

    def __dict_enums_to_strs__(self, d: dict) -> None:
        """
        Helper function that converts enum values in a dictionary into
        strings
        """

        for key in d.keys():
            if type(d[key]) is list:
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
        Helper function that cleans a dictionary containing a
        media list entry
        """

        if "mediaListEntry" not in d or d["mediaListEntry"] == None:
            return

        media_list_entry = d["mediaListEntry"]

        d["list_entry_status"] = media_list_entry["status"]
        d["progress"] = media_list_entry["progress"]
        d["score"] = (
            media_list_entry["score"] if media_list_entry["score"] != 0 else None
        )

        del d["mediaListEntry"]

        return None

    @validate_call
    def __filter_to_graphql__(
        self,
        base_query: str,
        filter: Union[MediaFilter, MediaListFilter],
    ) -> Tuple:
        """
        Adapter function that takes a base graphql string with variables,
        converts the filter into graphQL format, and replaces them

        @type base_query: str
        @type filter: MediaFilter | MediaListFilter
        @param base_query: graphQL base string
        @param format_args: number of args to replace in base query
        @param filter: a type of filter for media
        @rtype: Tuple
        @returns: tuple containing a resulting graphQL string and a variable map
        """

        variables = filter.model_dump(by_alias=True)
        not_none_variables = {key: value for (key, value) in variables.items() if value}

        variable_types = self.__create_var_type_map__(not_none_variables)

        self.__dict_enums_to_strs__(not_none_variables)
        self.__dict_dates_to_fuzzy__(not_none_variables)

        query_variables_string = ", ".join(
            ["$" + key + " : " + variable_types[key] for key in variable_types.keys()]
        )
        filters_string = ", ".join(
            [key + " : " + "$" + key for key in not_none_variables.keys()]
        )

        args = [query_variables_string, filters_string]

        query = base_query.format(*args)

        return (query, not_none_variables)

    @validate_call
    async def search(self, filters: MediaFilter) -> Tuple:
        """
        Function that queries anilist API for media filtered by filters

        @type filters: MediaFilter
        @param filters: TypedDict containing media filter key-value pairs
        @rtype: Tuple
        @returns: Tuple containing dictionaries representing the top 50 \
        media matching the filters and results info
        """

        data = await self.api.get_data(*self.__filter_to_graphql__(get_media, filters))

        results_info = data["data"]["Page"]["pageInfo"]
        data = data["data"]["Page"]["media"]

        # cleans data
        for i, entry in enumerate(data):
            for key in list(entry.keys()):
                # removes fields with no value
                if entry[key] == None:
                    del entry[key]
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

    @validate_call
    def __changes_to_graphql__(
        self, base_query: str, media_id: int, changes: ListEntryChanges
    ) -> Tuple:
        """
        Adapter function that takes a base graphql string with variables,
        converts the changes into graphQL format, and replaces them

        @type base_query: str
        @type media_id: int
        @type changes: ListEntryChanges
        @param base_query: graphQL base string
        @param changes: pending changes for a list entry
        @rtype: Tuple
        @returns: tuple containing a resulting graphQL string and a variable map
        """

        variables = changes.model_dump(by_alias=True)
        not_none_variables = {key: value for (key, value) in variables.items() if value}

        not_none_variables["mediaId"] = media_id

        variable_types = self.__create_var_type_map__(not_none_variables)

        self.__dict_enums_to_strs__(not_none_variables)
        self.__dict_dates_to_fuzzy__(not_none_variables)

        query_variables_string = ", ".join(
            ["$" + key + " : " + variable_types[key] for key in variable_types.keys()]
        )
        updates_string = ", ".join(
            [key + " : " + "$" + key for key in not_none_variables.keys()]
        )

        args = [query_variables_string, updates_string]

        query = base_query.format(*args)

        return (query, not_none_variables)

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
        @returns dict containing updated list entry info and None if the update could not be completed
        """

        data = await self.api.authenticated_call(
            *self.__changes_to_graphql__(update_entry, media_id, changes)
        )

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
            if data[key] == None:
                del data[key]

        return data

    @validate_call
    async def get_trending_media(self, media_type: MediaType) -> List[MediaPreview]:
        """
        Gets top 50 trending media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: List containing top 50 trending media
        """

        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.TRENDING_DESC]

        return (await self.search(media_filters))[0]

    @validate_call
    async def get_all_time_media(self, media_type: MediaType) -> List[MediaPreview]:
        """
        Gets top 50 all time media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: List containing top 50 all time media
        """

        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.POPULARITY_DESC]

        return (await self.search(media_filters))[0]

    @validate_call
    async def get_seasonal_media(self, media_type: MediaType) -> List[MediaPreview]:
        """
        Gets top 50 currently releasing media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: List containing top 50 releasing media
        """

        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.TRENDING_DESC]
        media_filters["media_status"] = MediaStatus.RELEASING

        return (await self.search(media_filters))[0]

    @validate_call
    async def get_upcoming_media(self, media_type: MediaType) -> List[MediaPreview]:
        """
        Gets top 50 not yet released media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: List containing top 50 upcoming media
        """
        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.POPULARITY_DESC]
        media_filters["media_status"] = MediaStatus.NOT_YET_RELEASED

        return (await self.search(media_filters))[0]

    @validate_call
    async def get_media_info(self, id: int) -> CompleteDocument:
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

        # removes fields with no value
        q = deque([(data, key) for key in data.keys()])

        while q:
            context, key = q.popleft()
            if type(context[key]) is dict:
                for key_v in context[key].keys():
                    q.append((context[key], key_v))
            else:
                if context[key] == None:
                    del context[key]

        # deletes remaining empty dictionaries
        q = deque([(data, key) for key in data.keys()])

        while q:
            context, key = q.popleft()
            if type(context[key]) is dict:
                if len(context[key]) == 0:
                    del context[key]
                else:
                    for key_v in context[key].keys():
                        q.append((context[key], key_v))

        if data["type"] == "ANIME":
            return Anime(**data)
        else:
            return Manga(**data)

    @validate_call
    async def get_media_list(
        self,
        user_name: str,
        media_type: MediaType,
        media_list_status: List[MediaListStatus],
    ) -> List[Tuple]:
        """
        Function that requests media lists based on function parameters

        @type user_name: str
        @type media_type: MediaType
        @type media_list_status: List[MediaListStatus]
        @param user_name: anilist username
        @param media_type: anime or manga
        @param media_list_status: list of media statuses
        @rtype: List[Tuple]
        @returns: List of tuples representing a media_list with info like length, status, etc.
        """

        list_filters = MediaListFilter()

        list_filters["user_name"] = user_name
        list_filters["media_type"] = media_type
        list_filters["status_in"] = media_list_status

        data = await self.api.get_data(
            *self.__filter_to_graphql__(get_media_list, list_filters)
        )

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
                    entry_objects.copy(),
                )
            )

        return results
