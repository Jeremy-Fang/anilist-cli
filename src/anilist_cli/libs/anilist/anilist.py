from pydantic import validate_call

from .models.media_filter import MediaFilter, media_filter_map
from .models.media_type import MediaType
from .models.media_sort import MediaSort
from .models.media_status import MediaStatus

from typing import List

from .queries import *

from ..cache.session_cache import SessionCache

import json
import aiohttp

ANILIST_URL = "https://graphql.anilist.co"


class AnilistAPI:
    """
    Facade providing simple interface to access the anilist api, while also
    incorporating caching

    Attributes:
    token: str anilist user access token
    _session: aiohttp client session used to make API requests
    _cache: session cache to store API request responses
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

    def _check_cache(self, query: str, variables: dict) -> List[dict] | None:
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

            return response["data"]["Page"]["media"]
        else:
            print("cache miss!")

        return None

    def _build_query_variables(self, media_filters: MediaFilter) -> List[dict]:
        """
        Converts media filters into format usable for GraphQL queries

        @type media_filter: MediaFilter
        @param media_filter: typed dict containing optional media filters
        @rtype: List[dict]
        @returns: list containing query variables and media filter variables
        """

        query_variables = {}
        media_filter_variables = {}

        for key in media_filters.keys():
            if type(media_filters[key]) is list:
                media_filter_variables[key] = []
                query_variables[key] = "[" + type(media_filters[key][0]).__name__ + "]"
                for entry in media_filters[key]:
                    media_filter_variables[key].append(entry.name)
            else:
                query_variables[key] = type(media_filters[key]).__name__
                media_filter_variables[key] = media_filters[key].name

        return [query_variables.copy(), media_filter_variables.copy()]

    @validate_call
    async def search_media(self, media_filters: MediaFilter) -> List[dict]:
        """
        Abstraction around media search queries, returning the first 50 entires

        @type media_filters: MediaFilter
        @param media_filters: filters for graphQL query
        @rtype: List[dict]
        @returns: dictionary containing top 50 results matching query and variables
        """

        # Following code turns dictionaries into graphql variable assignments
        query_variables, media_filter_variables = self._build_query_variables(
            media_filters
        )

        filters = [
            "$" + key + " : " + query_variables[key] for key in query_variables.keys()
        ]
        media_filters = [
            media_filter_map[key] + " : " + "$" + key for key in query_variables.keys()
        ]

        filters = ", ".join(filters)
        media_filters = ", ".join(media_filters)

        query = get_media.format(
            filters=filters,
            media_filters=media_filters,
            list_entry=media_list_entry_query if self.user else "",
        )

        # checks if the request data is already in the cache
        data = self._check_cache(query, media_filter_variables)

        if data:
            return data

        async with self._session.post(
            ANILIST_URL,
            json={"query": query, "variables": media_filter_variables},
            headers=self.headers,
        ) as response:
            data = await response.json()

            if response.status != 200:
                return None

            self.cache.set(query, media_filter_variables, self.user, data, self._v)

            return data["data"]["Page"]["media"]

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

        return await self.search_media(media_filters)

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

        return await self.search_media(media_filters)

    @validate_call
    async def get_seasonal_media(self, media_type: MediaType) -> List[dict]:

        media_filters = MediaFilter()
        media_filters["media_type"] = media_type
        media_filters["sort_by"] = [MediaSort.TRENDING_DESC]
        media_filters["status"] = MediaStatus.RELEASING

        return await self.search_media(media_filters)

    async def close(self) -> None:
        """
        Function that closes aiohttp client session
        """
        if not self._session.closed:
            await self._session.close()
