from pydantic import validate_call
import json
import aiohttp
from enum import Enum

from .models.filter import *

from .models.media_type import MediaType
from .models.media_sort import MediaSort
from .models.media_status import MediaStatus
from .models.media_list_status import MediaListStatus

from typing import List, Tuple

from .queries import *

from ..cache.session_cache import SessionCache

ANILIST_URL = "https://graphql.anilist.co"


class AnilistAPI:
    """
    Facade providing simple interface to access the anilist api, while also
    incorporating caching

    Attributes:
    token: str anilist user access token
    user: str anilist user name
    _session: aiohttp client session used to make API requests
    headers: headers to be sent with API requests
    cache: session cache to store API request responses
    _v: int denoting the number of anilist mutations made this session
    """

    def __init__(self) -> None:
        """
        Initialize the AnilistAPI object with no access token,
        a session cache, and a client session
        """

        self.token: str | None = None
        self.user: str | None = None
        self._session = aiohttp.ClientSession()
        self.headers = {}
        self.cache = SessionCache("query_cache.db")
        self._v = 0

    @validate_call
    async def login(self, access_token: str) -> dict | None:
        """
        Attempts to set access token for this session. Checks to see if the
        token is valid and then returns data about the user.

        @type access_token: str
        @param access_token: anilist access token
        @rtype: dict | None
        @returns: user info if the access token is valid
        """
        self.token = access_token
        self.headers = {"Authorization": f"Bearer {self.token}"}

        async with self._session.post(
            ANILIST_URL, json={"query": get_user}, headers=self.headers
        ) as response:
            data = await response.json()

            if response.status != 200:
                return None

            self.user = data["data"]["Viewer"]["name"]

            return data["data"]["Viewer"]

    def _build_query_variables(self, filter: Filter) -> Tuple:
        """
        Converts a dictionary of variables into a format usable for GraphQL queries

        @type filter: Filter
        @param filter: abstraction over filter TypedDicts and variable type maps
        @rtype: Tuple
        @returns: tuple containing custom strings to assign attributes in the graphQL query and media filter variables
        """

        graphql_map = filter.graphql_map
        variables = filter.filter

        query_variables = {}
        filter_variables = {}

        for key in variables.keys():
            if type(variables[key]) is list:
                filter_variables[key] = []
                query_variables[key] = "[" + type(variables[key][0]).__name__ + "]"
                for entry in variables[key]:
                    filter_variables[key].append(entry.name)
            else:
                if issubclass(type(variables[key]), Enum):
                    query_variables[key] = type(variables[key]).__name__
                    filter_variables[key] = variables[key].name
                else:
                    query_variables[key] = type_map[type(variables[key]).__name__]
                    filter_variables[key] = variables[key]

        query_variables_assignment = ", ".join(
            ["$" + key + " : " + query_variables[key] for key in query_variables.keys()]
        )
        filters_assignment = ", ".join(
            [graphql_map[key] + " : " + "$" + key for key in query_variables.keys()]
        )

        return (
            query_variables_assignment,
            filters_assignment,
            filter_variables.copy(),
        )

    def __check_cache(self, query: str, variables: dict) -> List[dict] | None:
        """
        Helper function that checks if the request is already in cache

        @type query: str
        @type variables: dict
        @param query: graphQL query
        @param variables: variables for graphQL query
        @rtype: List[dict] | None
        @returns: None if the cache missed, and the parsed response data if cache hit
        """

        data = self.cache.get(query, variables, self.user, self._v)

        if data:
            print("cache hit!")
            response = json.loads(data[3])

            return response
        else:
            print("cache miss!")

        return None

    def _check_cache(func):
        async def wrapper(self, *args, **kwargs):
            data = self.__check_cache(*args, **kwargs)

            if data:
                return data

            return await func(self, *args)

        return wrapper

    @_check_cache
    @validate_call
    async def get_data(self, query: str, variables: dict) -> List[dict]:
        """
        Abstraction around media search queries, returning the first 50 entires

        @type media_filters: MediaFilter
        @param media_filters: filters for graphQL query
        @rtype: List[dict]
        @returns: dictionary containing top 50 results matching query and variables
        """

        async with self._session.post(
            ANILIST_URL,
            json={"query": query, "variables": variables},
            headers=self.headers,
        ) as response:
            data = await response.json()

            if response.status != 200:
                return None

            self.cache.set(query, variables, self.user, data, self._v)

            return data

    @validate_call
    async def get_trending_media(self, media_type: MediaType) -> List[dict]:
        """
        Gets top 50 trending media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: dictionary containing top 50 trending media
        """

        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.TRENDING_DESC]

        filter = Filter(graphql_map=media_filter_map, filter=media_filters)

        (args, filters, variables) = self._build_query_variables(filter)

        query = get_media.format(
            args=args,
            filters=filters,
            list_entry=media_list_entry_preview if self.user else "",
        )

        data = await self.get_data(query, variables)

        return data["data"]["Page"]["media"]

    @validate_call
    async def get_all_time_media(self, media_type: MediaType) -> List[dict]:
        """
        Gets top 50 all time media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: dictionary containing top 50 all time media
        """

        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.POPULARITY_DESC]

        filter = Filter(graphql_map=media_filter_map, filter=media_filters)

        (args, filters, variables) = self._build_query_variables(filter)

        query = get_media.format(
            args=args,
            filters=filters,
            list_entry=media_list_entry_preview if self.user else "",
        )

        data = await self.get_data(query, variables)

        return data["data"]["Page"]["media"]

    @validate_call
    async def get_seasonal_media(self, media_type: MediaType) -> List[dict]:
        """
        Gets top 50 currently releasing media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: dictionary containing top 50 releasing media
        """

        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.TRENDING_DESC]
        media_filters["media_status"] = MediaStatus.RELEASING

        filter = Filter(graphql_map=media_filter_map, filter=media_filters)

        (args, filters, variables) = self._build_query_variables(filter)

        query = get_media.format(
            args=args,
            filters=filters,
            list_entry=media_list_entry_preview if self.user else "",
        )

        data = await self.get_data(query, variables)

        return data["data"]["Page"]["media"]

    @validate_call
    async def get_upcoming_media(self, media_type: MediaType) -> List[dict]:
        """
        Gets top 50 not yet released media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: dictionary containing top 50 upcoming media
        """
        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.POPULARITY_DESC]
        media_filters["status"] = MediaStatus.NOT_YET_RELEASED

        filter = Filter(graphql_map=media_filter_map, filter=media_filters)

        (args, filters, variables) = self._build_query_variables(filter)

        query = get_media.format(
            args=args,
            filters=filters,
            list_entry=media_list_entry_preview if self.user else "",
        )

        data = await self.get_data(query, variables)

        return data["data"]["Page"]["media"]

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

        (args, filters, variables) = self._build_query_variables(filter)

        query = get_expanded_media_info.format(
            args=args,
            filters=filters,
            list_entry=media_list_entry_preview if self.user else "",
        )

        data = await self.get_data(query, variables)

        return data["data"]["Media"]

    @validate_call
    async def search(self, filters: MediaFilter) -> List[dict]:
        filter = Filter(graphql_map=media_filter_map, filter=filters)

        (args, f, variables) = self._build_query_variables(filter)

        query = get_media.format(
            args=args,
            filters=f,
            list_entry=media_list_entry_preview if self.user else "",
        )

        data = await self.get_data(query, variables)

        return data["data"]["Page"]["media"]

    async def get_media_list(
        self, media_type: MediaType, media_list_status: List[MediaListStatus]
    ) -> List[dict]:
        list_filters = MediaListFilter()
        list_filters["user_name"] = "JeremyFang022"
        list_filters["media_type"] = media_type
        list_filters["status_in"] = media_list_status

        filter = Filter(graphql_map=media_list_filter_map, filter=list_filters)

        (args, filters, variables) = self._build_query_variables(filter)

        query = get_media_list.format(args=args, filters=filters)

        data = await self.get_data(query, variables)

        return data["data"]["MediaListCollection"]["lists"]

    async def close(self) -> None:
        """
        Function that closes aiohttp client session
        """
        if not self._session.closed:
            await self._session.close()
