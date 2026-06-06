import json
import logging

import aiohttp
from pydantic import validate_call

from ..cache.session_cache import SessionCache
from .queries import get_user

ANILIST_URL = "https://graphql.anilist.co"

logger = logging.getLogger(__name__)


class AnilistClient:
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
        Initialize the AnilistClient object with no access token,
        a session cache, and a client session
        """

        self.token: str | None = None
        self.user: str | None = None
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.headers: dict[str, str] = {}
        self.cache: SessionCache = SessionCache("query_cache.db")
        self._v: int = 0

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
        temp_headers = {"Authorization": f"Bearer {access_token}"}
        data = await self._post({"query": get_user}, headers=temp_headers)
        if data is None:
            return None

        self.token = access_token
        self.headers = temp_headers
        self.user = data["data"]["Viewer"]["name"]
        return data["data"]["Viewer"]

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

        cached = self._check_cache(query, variables)
        if cached is not None:
            return cached

        data = await self._post({"query": query, "variables": variables})
        if data is None:
            return None

        self.cache.set(query, variables, self.user, data, self._v)
        return data

    @validate_call
    async def authenticated_call(self, mutation: str, variables: dict) -> dict | None:
        """
        Abstraction around list entry mutations

        @type mutation: str
        @type variables: dict
        @param mutation: graphQL mutation request
        @param variables: key-value variables for the mutation
        @rtype: dict | None
        @returns: dictionary containing updated data
        """

        if self.token is None:
            return None

        data = await self._post({"query": mutation, "variables": variables})
        if data is None:
            return None

        self._v += 1
        return data

    async def close(self) -> None:
        """
        Function that closes aiohttp client session
        """
        if not self._session.closed:
            await self._session.close()

    async def _post(
        self, payload: dict, headers: dict[str, str] | None = None
    ) -> dict | None:
        """
        Private helper that makes a POST request and handles status checking

        @type payload: dict
        @type headers: dict[str, str] | None
        @param payload: JSON payload for the request
        @param headers: request headers, defaults to self.headers if not provided
        @rtype: dict | None
        @returns: parsed response JSON, or None if the request failed
        """
        async with self._session.post(
            ANILIST_URL, json=payload, headers=headers if headers is not None else self.headers
        ) as response:
            if response.status != 200:
                logger.warning(
                    "AniList API error %d: %s",
                    response.status,
                    await response.text(),
                )
                return None
            return await response.json()

    def _check_cache(self, query: str, variables: dict) -> dict | None:
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

        if data is not None:
            return json.loads(data["data"])

        return None
