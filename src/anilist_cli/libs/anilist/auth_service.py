from keyring.credentials import Credential

from anilist_cli.libs.anilist.client import AnilistClient
from anilist_cli.utils import auth_util


class AuthService:
    def __init__(self, client: AnilistClient) -> None:
        self._client = client

    async def login(self, token: str) -> str | None:
        await self._client.login(token)
        return self._client.user

    async def perform_oauth_flow(self) -> tuple[str, str]:
        return await auth_util.perform_oauth_flow()

    def get_credential(self) -> Credential | None:
        return auth_util.get_credential()

    def logout(self) -> bool:
        return auth_util.delete_access_token()
