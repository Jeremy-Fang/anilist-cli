from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label

from anilist_cli.libs.anilist.auth_service import AuthService


class LoginScreen(Screen[tuple[str, str]]):
    def __init__(self, auth_service: AuthService) -> None:
        super().__init__()
        self._auth_service = auth_service

    def compose(self) -> ComposeResult:
        yield Label("AniList CLI")
        yield Button("Login with AniList", id="login")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "login":
            event.button.disabled = True
            self._do_login()

    @work
    async def _do_login(self) -> None:
        try:
            result = await self._auth_service.perform_oauth_flow()
            self.dismiss(result)
        except RuntimeError as e:
            self.notify(str(e), severity="error")
            self.query_one("#login", Button).disabled = False
