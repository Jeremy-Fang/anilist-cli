from pydantic import validate_call

from .models.media_filter import MediaFilter
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

    def _check_cache(func):
        """
        Decorator to check if the function response has been cached
        """

        async def wrapper(self, *args, **kwargs):
            data = self.cache.get(args[0], args[1], self.user, self._v)

            if data:
                print("cache hit!")
                response = json.loads(data[3])

                return response["data"]["Page"]["media"]
            else:
                print("cache miss!")
                return await func(self, *args, **kwargs)

        return wrapper

    @validate_call
    @_check_cache
    async def search_media(self, query: str, variables: dict = {}) -> List[dict]:
        """
        Abstraction around media search queries, returning the first 50 entires

        @type query: str
        @type variables: dict
        @param query: graphQL query to anilist API
        @param variables: graphQL variables
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
        media_filters["sort"] = [MediaSort.TRENDING_DESC, MediaSort.FAVOURITES_DESC]

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

        print(query_variables)
        print(media_filter_variables)
        # return await self.search_media(get_sorted_media, variables)

        return []

    @validate_call
    async def get_all_time_media(self, media_type: MediaType) -> List[dict]:
        """
        Gets top 50 all time media

        @type media_type: MediaType
        @param media_type: anime or manga
        @rtype: List[dict]
        @returns: dictionary containing top 50 all time media
        """

        variables = {"type": media_type.name, "sort": MediaSort.POPULARITY_DESC.name}

        return await self.search_media(get_sorted_media, variables)

    @validate_call
    async def get_seasonal_media(self, media_type: MediaType) -> List[dict]:

        variables = {
            "type": media_type.name,
            "sort": MediaSort.TRENDING_DESC.name,
            "status": MediaStatus.RELEASING.name,
        }

        return await self.search_media(get_seasonal_media, variables)

    async def close(self) -> None:
        """
        Function that closes aiohttp client session
        """
        if not self._session.closed:
            await self._session.close()
