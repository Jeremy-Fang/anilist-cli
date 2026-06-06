import json
from collections.abc import Callable
from typing import Any

import aiohttp
from pydantic import validate_call

from ..cache.session_cache import SessionCache
from .queries import get_user

ANILIST_URL = "https://graphql.anilist.co"


def _check_cache_(func: Callable) -> Callable:
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        data = self.__check_cache__(*args, **kwargs)

        if data:
            return data

        return await func(self, *args)

    return wrapper


class AnilistAPI:
    """
    API class encapsulating the anilist API functionality

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

    def __check_cache__(self, query: str, variables: dict) -> dict | None:
        """
        Helper function that checks if the request is already in cache

        @type query: str
        @type variables: dict
        @param query: graphQL query
        @param variables: variables for graphQL query
        @rtype: dict | None
        @returns: None if the cache missed, and the parsed response data if cache hit
        """

        data = self.cache.get(query, variables, self.user, self._v)

        if data:
            return json.loads(data["data"])

        return None

    @_check_cache_
    @validate_call
    async def get_data(self, query: str, variables: dict) -> dict | None:
        """
        Abstraction around get queries

        @type query: str
        @type variables: dict
        @param query: graphQL query request
        @param variables: key-value variables for the query
        @rtype: dict | None
        @returns: full response dict from the AniList API
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
    async def authenticated_call(self, mutation: str, variables: dict) -> dict | None:
        """
        Abstraction around list entry mutations

        @type query: str
        @type variables: dict
        @param mutation: graphQL mutation request
        @param variables: key-value variables for the mutation
        @rtype: dict | None
        @returns: dictionary containing updated data
        """

        if self.token is None:
            return None

        async with self._session.post(
            ANILIST_URL,
            json={"query": mutation, "variables": variables},
            headers=self.headers,
        ) as response:
            data = await response.json()

            if response.status != 200:
                return None

            return data

    async def close(self) -> None:
        """
        Function that closes aiohttp client session
        """
        if not self._session.closed:
            await self._session.close()
