from .anilist import AnilistAPI

import json

from enum import Enum

from .models.filter import *

from .models.enums import *

from typing import List, Tuple

from .queries import *

from pydantic import validate_call

basic_type_map = {"str": "String", "int": "Int", "float": "Float", "bool": "Boolean"}


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
        self, base_query: str, format_args: int, filter: Filter
    ) -> Tuple:
        """
        Adapter function that takes a base graphql string with variables,
        converts the filter into graphQL format, and replaces them

        @type base_query: str
        @type format_args: int
        @type filter: Filter
        @param base_query: graphQL base string
        @param filter: abstraction over filter TypedDicts
        @rtype: Tuple
        @returns: tuple containing a resulting graphQL string and a variable map
        """

        variables = filter.filter.model_dump(by_alias=True)
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

        if format_args == 3:
            args.append(self.api.user if self.api.user else "")

        query = base_query.format(*args)

        return (query, not_none_variables)

    @validate_call
    async def search(self, filters: MediaFilter) -> List[dict]:
        """
        Function that queries anilist API for media filtered by filters

        @type filters: MediaFilter
        @param filters: TypedDict containing media filter key-value pairs
        @rtype: List[dict]
        @returns: List containing up to 50 dictionaries representing media
        """

        filter = Filter(graphql_map=media_filter_map, filter=filters)

        data = await self.api.get_data(*self._filter_to_grapql(get_media, 3, filter))
        data = data["data"]["Page"]["media"]
        results = []

        # if filters[]
        # for row in data:
        #     print()
        return data

    @validate_call
    async def get_trending_media(self, media_type: MediaType) -> List[dict]:
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
    async def get_all_time_media(self, media_type: MediaType) -> List[dict]:
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
    async def get_seasonal_media(self, media_type: MediaType) -> List[dict]:
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
    async def get_upcoming_media(self, media_type: MediaType) -> List[dict]:
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
    async def get_media_info(self, id: int) -> dict | None:
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

        filter = Filter(graphql_map=media_filter_map, filter=media_filters)

        data = await self.api.get_data(
            *self._filter_to_grapql(get_expanded_media_info, 3, filter)
        )

        return data["data"]["Media"]

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

        filter = Filter(graphql_map=media_list_filter_map, filter=list_filters)

        data = await self.api.get_data(
            *self._filter_to_grapql(get_media_list, 2, filter)
        )

        return data["data"]["MediaListCollection"]["lists"]
