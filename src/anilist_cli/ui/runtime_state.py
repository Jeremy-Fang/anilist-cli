from anilist_cli.libs.anilist.adapter import AnilistAdapter
from anilist_cli.libs.anilist.auth_service import AuthService
from anilist_cli.libs.anilist.client import AnilistClient
from anilist_cli.libs.anilist.service import AnilistService


class RuntimeState:
    def __init__(self) -> None:
        self.client = AnilistClient()
        self.adapter = AnilistAdapter(self.client)
        self.service = AnilistService(self.adapter)
        self.auth_service = AuthService(self.client)
        self.username: str | None = None

    async def close(self) -> None:
        await self.client.close()
