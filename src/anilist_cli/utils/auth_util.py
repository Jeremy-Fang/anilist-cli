import os

import aiohttp
import keyring
from dotenv import load_dotenv
from keyring.credentials import Credential

from anilist_cli.utils import web_util

load_dotenv()

KEYRING_SERVICE = "Anilist"
CLIENT_ID = 21872
PORT = 8765
CALLBACK_PATH = "/callback"
REDIRECT_URI = f"http://localhost:{PORT}{CALLBACK_PATH}"


def get_credential() -> Credential | None:
    return keyring.get_credential(KEYRING_SERVICE, None)


def set_access_token(username: str, token: str) -> bool:
    keyring.set_password(KEYRING_SERVICE, username, token)
    return True


async def perform_oauth_flow() -> tuple[str, str]:
    client_secret = os.getenv("ANILIST_CLIENT_SECRET")
    if client_secret is None:
        raise RuntimeError("ANILIST_CLIENT_SECRET not set in .env")

    auth_url = (
        f"https://anilist.co/api/v2/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
    )
    web_util.open_browser(auth_url)

    auth_code = await web_util.run_callback_server(PORT, path=CALLBACK_PATH)
    if auth_code is None:
        raise RuntimeError("OAuth callback did not return an auth code")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://anilist.co/api/v2/oauth/token",
            json={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": client_secret,
                "redirect_uri": REDIRECT_URI,
                "code": auth_code,
            },
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Token exchange failed: HTTP {resp.status}")
            token_data = await resp.json()
            access_token: str = token_data["access_token"]

        async with session.post(
            "https://graphql.anilist.co",
            json={"query": "{ Viewer { name } }"},
            headers={"Authorization": f"Bearer {access_token}"},
        ) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Viewer query failed: HTTP {resp.status}")
            viewer_data = await resp.json()
            username: str = viewer_data["data"]["Viewer"]["name"]

    set_access_token(username, access_token)
    return username, access_token


def delete_access_token() -> bool:
    credential = get_credential()

    if not credential:
        return False

    keyring.delete_password(KEYRING_SERVICE, credential.username)

    return True
