# anilist-cli

A CLI tool for browsing and managing your AniList anime/manga lists from the terminal.

## Commands

```bash
uv sync              # install dependencies (creates .venv automatically)
uv run anilist_cli   # run the app
uv run pytest        # run tests
uv run ruff check src/    # lint
uv run pyright src/       # type check
```

## Architecture

Five-layer design:

- **`AnilistClient`** (`libs/anilist/client.py`) — raw async HTTP client wrapping the AniList GraphQL API
- **`AnilistAdapter`** (`libs/anilist/adapter.py`) — translates between Python objects (filters, models) and GraphQL queries/variables; parses raw API responses into model instances
- **`AnilistService`** (`libs/anilist/service.py`) — data operations layer; owns preset queries (trending, seasonal, etc.) and delegates raw operations to `AnilistAdapter`
- **`AuthService`** (`libs/anilist/auth_service.py`) — session management layer; owns OAuth flow, login, logout, and credential retrieval. Distinct from `AnilistService` because auth is not a data operation — it sets up the session that data operations depend on
- **Models** — Pydantic models organized in an inheritance hierarchy: `Media` + `ListEntry` → `CompleteDocument` → `Anime` / `Manga`; `MediaPreview` → `AnimePreview` / `MangaPreview`

Screens interact with `AnilistService` and `AuthService` only — never with `AnilistAdapter` or `AnilistClient` directly.

GraphQL queries live as static `.graphql` files under `libs/anilist/queries/` and are loaded at import time by `queries.py`. Variables are passed as a plain dict; Pydantic's `model_dump(by_alias=True)` handles the Python snake_case → GraphQL camelCase mapping via `Field(alias=...)` on each model field.

## Caching

Responses are cached in a local SQLite database (`query_cache.db`) keyed by `(query, variables, user)`. Cache entries expire after a TTL and are also invalidated by a version counter (`_v` on `AnilistClient`) that is incremented after every successful mutation via `authenticated_call`.

The SQLite cache was chosen as a learning exercise — an in-memory dict or a TTL cache (`cachetools`, `aiocache`) would also work for a short-lived CLI process.

## Tooling Notes

Uses `uv` for dependency management (replaces Poetry). `uv sync` auto-creates `.venv` in the project root using Python 3.13. Pyright is configured to find it via `venvPath = "."` and `venv = ".venv"` in `pyproject.toml`.

## Testing

Unit tests use manual mocks (inline Python dicts) rather than VCR/recorded cassettes. VCR was ruled out because stale cassettes silently pass against outdated API responses when AniList changes a response shape — catching that requires extra infrastructure (scheduled live runs) not worth adding at this stage. Integration tests are deferred until the feature set stabilizes; when added, they should use real read-only API calls with a test account token in GitHub secrets rather than cassettes.

Frontend screens are tested via Textual's `Pilot` API. `AuthService` and `AnilistService` are mocked at the screen boundary — no true E2E testing.

## Frontend

**Decision: Textual** (not InquirerPy). Textual is async-first (built on asyncio), which means the async API layer integrates without workarounds. `@work` decorators run coroutines as background tasks without blocking the UI. InquirerPy is sync-only — keeping it would require a persistent manually-managed event loop and `loop.run_until_complete()` calls at every screen transition, which is fiddly and fragile.

**Current structure:**
```
src/anilist_cli/
├── main.py                   # entry point — runs AnilistApp().run()
├── models/
│   └── cli_state.py          # screen inventory — delete once all screens are implemented
├── ui/
│   ├── app.py                # Textual App subclass
│   ├── runtime_state.py      # dependency container: owns AnilistClient, AnilistAdapter, AnilistService, AuthService, username
│   └── screens/              # one Screen subclass per view
│       ├── login.py
│       ├── main_menu.py      # not yet implemented
│       ├── search.py         # not yet implemented
│       ├── media_info.py     # not yet implemented
│       └── ...
├── utils/
│   ├── auth_util.py          # OAuth flow, keyring helpers; all OAuth constants live here
│   └── web_util.py           # generic stateless I/O: open_browser(), run_callback_server()
└── libs/
```

**Remaining refactors before screens are complete:**

- **`CLIState` gets deleted.** Textual tracks the screen stack natively via `push_screen` / `pop_screen`. `models/cli_state.py` is kept as a screen inventory reference until all screens are implemented, then removed.
- **InquirerPy can be removed** once all screens are ported to Textual widgets.

## Screen / App Design Decisions

- **`RuntimeState` is a dependency container**, not a Textual component. It groups `AnilistClient`, `AnilistAdapter`, `AnilistService`, `AuthService`, and `username` so `AnilistApp` doesn't accumulate a dozen flat attributes. Screens never access `RuntimeState` directly.

- **`RuntimeState` is created in `on_mount`, not `__init__`.** `AnilistClient.__init__()` creates an `aiohttp.ClientSession`, which must be created inside a running event loop. `on_mount` is async and guaranteed to run inside Textual's event loop.

- **Constructor injection for services.** Screens receive only the service(s) they need, passed as constructor arguments by the app (or by the pushing screen). Screens must not access `self.app.runtime_state` — that would couple the view to the controller's internals.

- **App mediates only boundary transitions.** `AnilistApp` only needs a callback when a screen result must update `RuntimeState` (e.g., `_on_login` stores the username and sets up the client session). Pure navigation — where no shared state changes — is handled by screens pushing/popping other screens directly via `self.app.push_screen()`.

- **Services flow through the screen stack.** When Screen A pushes Screen B and Screen B needs a service, Screen A must already hold a reference to that service and pass it in Screen B's constructor. Screens must not reach into `self.app` to retrieve services — doing so couples the view to the controller.

- **`perform_oauth_flow()` returns `(username, token)`.** Both values are needed immediately after the OAuth flow — returning them together avoids a redundant keyring lookup in `_on_login`.

- **`web_util.py` is generic and stateless.** `open_browser(url)` and `run_callback_server(port, path)` accept all values as parameters. All AniList-specific OAuth constants (`CLIENT_ID`, `PORT`, `CALLBACK_PATH`, `REDIRECT_URI`) live in `auth_util.py`.

- **OAuth uses authorization code flow** (not implicit grant). AniList rejects implicit grant with custom redirect URIs. A local `aiohttp` server on port 8765 captures the redirect. Port 8765 is fixed because AniList requires the redirect URI to be registered statically. Client secret is stored in `.env` (gitignored).

## Open UML Design Questions (no decisions made yet)

- **`CompleteDocument` and `MediaPreview` inheriting from `ListEntry`** — conflates media identity with user list interaction. A logged-out user has `Media` data but no `ListEntry` data; modeling this as inheritance means all `ListEntry` fields are `None` noise on the object for non-logged-in users. Composition may be more accurate: `CompleteDocument` extends only `Media` and carries `list_entry: ListEntry | None`. This also matches the AniList API response shape (media with an optional nested `mediaListEntry`). No decision made.
- **`MediaListEntry` not inheriting from `Media`** — every other concrete class with media data (`Anime`, `Manga`, `MediaPreview`, `AnimePreview`, `MangaPreview`) inherits from `Media`. `MediaListEntry` defines `id`, `media_id`, and `title` directly instead, which is structurally inconsistent. No decision made.
- **`AnimePreview` / `MangaPreview` as empty subclasses** — neither adds fields or methods over `MediaPreview`. The only value is distinct types for isinstance checks. Consider whether a single `MediaPreview` with a `media_type` field would be simpler, or whether anime/manga-specific preview fields are planned. No decision made.
- **`notes` vs `note` naming** — `ListEntry` has `notes` (plural), `ListEntryChanges` has `note` (singular). These represent the same concept and should be consistent. No decision made.
- **`adapter: Any` typing on `ListEntry`** — the most critical dependency in the model layer bypasses all type checking. Should be typed against a Protocol after the Active Record pattern is removed. No decision made.

## Known Gotchas

- `ListEntry` currently holds `adapter: AnilistAdapter` so models can call `update_list_entry()` on themselves (Active Record pattern). This creates a circular dependency and couples models to the network layer. Deferred refactor: move `update_list_entry()` and `add_changes()` to `AnilistService` and make models pure data. The resulting hierarchy reads cleanly: `AnilistClient` (raw HTTP) → `AnilistAdapter` (parsing) → `AnilistService` (business logic) → Models (pure data).

- Several deferred DRY/maintainability cleanups remain in `adapter.py` — low priority since they don't affect correctness:
  - `search` iterates `data` twice (transform then construct) — merge into one loop
  - `_dict_enums_to_strs` builds a list with a `for` loop + `.copy()` — replace with a list comprehension
  - `update_list_entry` repeats a rename-then-delete key pattern three times — collapse with `data.pop()`
  - `update_list_entry` uses `type(data[key]) is dict` — should be `isinstance` for consistency and subclass correctness

- **Future migration: `ariadne-codegen`** — generates fully-typed Python client code from `.graphql` files and the AniList schema. Would replace `AnilistAdapter`'s hand-written parsing, `model_dump(by_alias=True)` variable mapping, and the `Field(alias=...)` workarounds. Worth tracking once the feature set stabilises.
