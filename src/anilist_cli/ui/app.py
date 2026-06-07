from textual.app import App

from anilist_cli.ui.runtime_state import RuntimeState
from anilist_cli.ui.screens.login import LoginScreen


class AnilistApp(App[None]):
    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self.runtime_state: RuntimeState | None = None

    async def on_mount(self) -> None:
        self.runtime_state = RuntimeState()
        credential = self.runtime_state.auth_service.get_credential()
        if credential is not None:
            self.runtime_state.username = await self.runtime_state.auth_service.login(
                credential.password
            )
            # TODO: push main menu screen
        else:
            self.push_screen(
                LoginScreen(self.runtime_state.auth_service), self._on_login
            )

    async def _on_login(self, result: tuple[str, str] | None) -> None:
        if result is None:
            return
        assert self.runtime_state is not None
        username, token = result
        await self.runtime_state.auth_service.login(token)
        self.runtime_state.username = username
        self.notify(f"Logged in as {username}")
        # TODO: push main menu screen

    async def on_unmount(self) -> None:
        if self.runtime_state is not None:
            await self.runtime_state.close()
