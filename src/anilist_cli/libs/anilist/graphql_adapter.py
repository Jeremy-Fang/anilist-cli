from .anilist import AnilistAPI

import json

from enum import Enum

from .models.filter import *
from .models.enums import *
from .models.media_title import MediaTitle

from .models.media_preview import MediaPreview
from .models.anime_preview import AnimePreview
from .models.manga_preview import MangaPreview

from .models.complete_document import CompleteDocument

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

    @validate_call
    def _filter_to_grapql(
        self,
        base_query: str,
        format_args: int,
        filter: Union[MediaFilter, MediaListFilter],
    ) -> Tuple:
        """
        Adapter function that takes a base graphql string with variables,
        converts the filter into graphQL format, and replaces them

        @type base_query: str
        @type format_args: int
        @type filter: MediaFilter | MediaListFilter
        @param base_query: graphQL base string
        @param format_args: number of args to replace in base query
        @param filter: a type of filter for media
        @rtype: Tuple
        @returns: tuple containing a resulting graphQL string and a variable map
        """

        variables = filter.model_dump(by_alias=True)
        not_none_variables = {key: value for (key, value) in variables.items() if value}

        variable_types = {}

        # creates map for type of each filter
        for key in not_none_variables.keys():
            if type(not_none_variables[key]) is list:
                if issubclass(type(not_none_variables[key][0]), Enum):
                    variable_types[key] = (
                        "[" + type(not_none_variables[key][0]).__name__ + "]"
                    )
                else:
                    variable_types[key] = (
                        "["
                        + basic_type_map[type(not_none_variables[key][0]).__name__]
                        + "]"
                    )
            else:
                if issubclass(type(not_none_variables[key]), Enum):
                    variable_types[key] = type(not_none_variables[key]).__name__
                else:
                    variable_types[key] = basic_type_map[
                        type(not_none_variables[key]).__name__
                    ]

        # maps enum values to their names for filters
        for key in not_none_variables.keys():
            if type(not_none_variables[key]) is list:
                if issubclass(type(not_none_variables[key][0]), Enum):
                    val = []
                    for entry in not_none_variables[key]:
                        val.append(entry.name)
                    not_none_variables[key] = val.copy()
            else:
                if issubclass(type(not_none_variables[key]), Enum):
                    not_none_variables[key] = not_none_variables[key].name

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
    async def search(self, filters: MediaFilter) -> List[MediaPreview]:
        """
        Function that queries anilist API for media filtered by filters

        @type filters: MediaFilter
        @param filters: TypedDict containing media filter key-value pairs
        @rtype: List[dict]
        @returns: List containing up to 50 dictionaries representing media
        """

        data = await self.api.get_data(*self._filter_to_grapql(get_media, 2, filters))

        data = data["data"]["Page"]["media"]

        # cleans data
        for entry in data:
            for key in list(entry.keys()):
                # removes fields with no value
                if entry[key] == None:
                    del entry[key]
            entry["api"] = self
            entry["title"] = MediaTitle(**entry["title"])
            entry["status"] = MediaStatus[entry["status"]]
            entry["format"] = MediaFormat[entry["format"]]
            entry["type"] = MediaType[entry["type"]]

            if "mediaListEntry" in entry:
                media_list_entry = entry["mediaListEntry"]
                # removes fields with no value
                for key in list(media_list_entry.keys()):
                    if media_list_entry[key] == None:
                        del media_list_entry[key]

                entry["list_entry_status"] = MediaListStatus[media_list_entry["status"]]
                entry["progress"] = media_list_entry["progress"]
                entry["score"] = (
                    media_list_entry["score"]
                    if media_list_entry["score"] != 0
                    else None
                )

        results = []

        for entry in data:
            if entry["type"] == MediaType.ANIME:
                results.append(AnimePreview(**entry))
            else:
                results.append(MangaPreview(**entry))

        return results

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

        return await self.search(media_filters)

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

        return await self.search(media_filters)

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

        return await self.search(media_filters)

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
        media_filters["status"] = MediaStatus.NOT_YET_RELEASED

        return await self.search(media_filters)

    @validate_call
    async def get_media_info(self, id: int) -> CompleteDocument:
        """
        Function that gets detailed information on a media entry matching
        the id

        @type id: int
        @param id: id of media
        @rtype: dict | None
        @returns: dictionary containing detailed information on the matching media
        """

        media_filters = MediaFilter()
        media_filters["media_id"] = id

        data = await self.api.get_data(
            *self._filter_to_grapql(get_expanded_media_info, 2, media_filters)
        )

        data = data["data"]["Media"]

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

        data["api"] = self
        data["title"] = MediaTitle(**data["title"])
        data["status"] = MediaStatus[data["status"]]
        data["format"] = MediaFormat[data["format"]]
        data["type"] = MediaType[data["type"]]
        data["source"] = MediaSource[data["source"]]

        if "season" in data:
            data["season"] = MediaSeason[data["season"]]

        if "startDate" in data:
            if len(data["startDate"]) == 3:
                data["startDate"] = date(**data["startDate"])
            else:
                del data["startDate"]

        if "endDate" in data:
            if len(data["endDate"]) == 3:
                data["endDate"] = date(**data["endDate"])
            else:
                del data["endDate"]

        if "description" in data:
            data["description"] = re.sub(CLEANR, "", data["description"])

        for i, genre in enumerate(data["genres"]):
            data["genres"][i] = MediaGenre[
                "_".join(genre.upper().replace("-", " ").split())
            ]

        if "mediaListEntry" in data:
            media_list_entry = data["mediaListEntry"]

            data["list_entry_status"] = MediaListStatus[media_list_entry["status"]]
            data["progress"] = media_list_entry["progress"]
            data["score"] = (
                media_list_entry["score"] if media_list_entry["score"] != 0 else None
            )

        return data

    @validate_call
    async def get_media_list(
        self,
        user_name: str,
        media_type: MediaType,
        media_list_status: List[MediaListStatus],
    ) -> List[dict]:
        """
        Function that requests media lists based on function parameters

        @type user_name: str
        @type media_type: MediaType
        @type media_list_status: List[MediaListStatus]
        @param user_name: anilist username
        @param media_type: anime or manga
        @param media_list_status: list of media statuses
        @rtype: List[dict]
        @returns: list of dictionaries representing media lists
        """

        list_filters = MediaListFilter()

        list_filters["user_name"] = user_name
        list_filters["media_type"] = media_type
        list_filters["status_in"] = media_list_status

        data = await self.api.get_data(
            *self._filter_to_grapql(get_media_list, 2, list_filters)
        )

        return data["data"]["MediaListCollection"]["lists"]
