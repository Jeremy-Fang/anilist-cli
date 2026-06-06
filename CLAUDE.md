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

Three-layer design:

- **`AnilistClient`** — raw async HTTP client wrapping the AniList GraphQL API
- **`GraphQLAdapter`** — translates between Python objects (filters, models) and GraphQL query strings/variables
- **Models** — Pydantic models organized in an inheritance hierarchy: `Media` + `ListEntry` → `CompleteDocument` → `Anime` / `Manga`; `MediaPreview` → `AnimePreview` / `MangaPreview`

## Caching

Responses are cached in a local SQLite database (`query_cache.db`) keyed by `(query, variables, user)`. Cache entries expire after a TTL and are also invalidated by a version counter (`_v` on `AnilistClient`) that is incremented after every successful mutation via `authenticated_call`.

The SQLite cache was chosen as a learning exercise — an in-memory dict or a TTL cache (`cachetools`, `aiocache`) would also work for a short-lived CLI process.

## Tooling Notes

Uses `uv` for dependency management (replaces Poetry). `uv sync` auto-creates `.venv` in the project root using Python 3.13. Pyright is configured to find it via `venvPath = "."` and `venv = ".venv"` in `pyproject.toml`.

## Testing

Unit tests use manual mocks (inline Python dicts) rather than VCR/recorded cassettes. VCR was ruled out because stale cassettes silently pass against outdated API responses when AniList changes a response shape — catching that requires extra infrastructure (scheduled live runs) not worth adding at this stage. Integration tests are deferred until the feature set stabilizes; when added, they should use real read-only API calls with a test account token in GitHub secrets rather than cassettes.

## Frontend

**Decision: Textual** (not InquirerPy). Textual is async-first (built on asyncio), which means the async API layer integrates without workarounds. `@work` decorators run coroutines as background tasks without blocking the UI. InquirerPy is sync-only — keeping it would require a persistent manually-managed event loop and `loop.run_until_complete()` calls at every screen transition, which is fiddly and fragile.

**Target structure:**
```
src/anilist_cli/
├── main.py                   # creates RuntimeState, mounts the Textual App
├── models/
│   └── cli_state.py          # to be deleted (see below)
├── ui/
│   ├── app.py                # Textual App subclass
│   ├── runtime_state.py      # owns AnilistClient, user session
│   └── screens/              # one Screen subclass per view
│       ├── login.py
│       ├── main_menu.py
│       ├── search.py
│       ├── media_info.py
│       └── ...
├── utils/
└── libs/
```

**Deferred refactors required before building screens:**

- **Service layer refactor is blocking.** Screens should call `AnilistService` methods and receive pure data objects — the Active Record pattern (models calling the API directly) breaks down in a UI context where multiple screens may trigger updates. Do this before writing any screens.
- **`CLIState` gets deleted.** Textual tracks the screen stack natively via `push_screen` / `pop_screen`. There is no separate state variable to maintain. Each `CLIState` value becomes a `Screen` subclass; `models/cli_state.py` is removed.
- **`RuntimeState` must own the `AnilistClient` instance and call `close()` on app exit.** Textual runs a single event loop for the entire app lifetime, so the `aiohttp.ClientSession` created inside `AnilistClient.__init__()` naturally lives as long as `RuntimeState` holds the reference — no session injection or parameter changes needed. The only reason to inject the session from outside would be for unit testability (passing a mock session), which is a separate concern.
- **InquirerPy can be removed** once all screens are ported to Textual widgets. `prompt_with_pages` in `inquirer_util.py` becomes a Textual `ListView` or `Select` widget with custom keybindings.

## Open UML Design Questions (no decisions made yet)

- **`CompleteDocument` and `MediaPreview` inheriting from `ListEntry`** — conflates media identity with user list interaction. A logged-out user has `Media` data but no `ListEntry` data; modeling this as inheritance means all `ListEntry` fields are `None` noise on the object for non-logged-in users. Composition may be more accurate: `CompleteDocument` extends only `Media` and carries `list_entry: ListEntry | None`. This also matches the AniList API response shape (media with an optional nested `mediaListEntry`). No decision made.
- **`MediaListEntry` not inheriting from `Media`** — every other concrete class with media data (`Anime`, `Manga`, `MediaPreview`, `AnimePreview`, `MangaPreview`) inherits from `Media`. `MediaListEntry` defines `id` and `title` directly instead, which is structurally inconsistent and is the root of the known `media_id` bug. No decision made.
- **`AnimePreview` / `MangaPreview` as empty subclasses** — neither adds fields or methods over `MediaPreview`. The only value is distinct types for isinstance checks. Consider whether a single `MediaPreview` with a `media_type` field would be simpler, or whether anime/manga-specific preview fields are planned. No decision made.
- **`notes` vs `note` naming** — `ListEntry` has `notes` (plural), `ListEntryChanges` has `note` (singular). These represent the same concept and should be consistent. No decision made.
- **`adapter: Any` typing on `ListEntry`** — the most critical dependency in the model layer bypasses all type checking. Should be typed against a Protocol after the `AnilistClient` / `AnilistService` refactor. No decision made.
- **`ListEntry → AnilistClient` connection in UML** — should be removed from the diagram once the service layer refactor is done, since models will no longer hold an API reference.

## Known Gotchas

- `RuntimeState` (not yet implemented) must NOT declare `session_cache` as a direct attribute — access it via `anilist_session.cache` instead. The UML diagram shows both, but the direct attribute is redundant and risks two paths to the same object being used inconsistently
- `ListEntry` currently holds `api: AnilistClient` so models can call `update_media_entry()` on themselves (Active Record pattern). This creates a circular dependency and couples models to the network layer. Deferred refactor: move `update_media_entry()` and `add_change()` to `GraphQLAdapter` (Service Layer pattern) and make models pure data. This is the industry-standard approach for API clients and CLI tools, and fits the existing three-layer architecture naturally. As part of this refactor, rename `GraphQLAdapter` → `AnilistService` — "Adapter" undersells the service layer responsibility and "GraphQL" exposes an implementation detail the caller shouldn't know about. (`AnilistAPI` has already been renamed to `AnilistClient`.) The resulting hierarchy reads cleanly: `AnilistClient` (raw HTTP) → `AnilistService` (business logic) → Models (pure data)

- `queries.py` stores GraphQL queries as Python format strings with `{variables}`, `{page_query}`, `{media_query}` placeholders — these are not valid GraphQL and cannot be validated by tooling. Deferred refactor: migrate to `.graphql` files (one file per query, real GraphQL syntax, no `{{}}` escaping). This forces static queries — all variables declared upfront, unused ones passed as `null` — which AniList handles gracefully. The payoff is that `__create_var_type_map__`, `__format_query__`, and the entire format string injection machinery in `GraphQLAdapter` can be deleted; the adapter just passes the variables dict directly. Setup requires a `queries/` subdirectory, loading files via `Path(__file__).parent / name).read_text()`, and adding `"**/*.graphql"` to `[tool.setuptools.package-data]` in `pyproject.toml`. Optionally pair with the GraphQL VSCode extension and a downloaded AniList schema for inline validation and field autocompletion.

- Private helper methods in `graphql_adapter.py` currently use `__dunder__` naming (e.g. `__create_var_type_map__`, `__format_query__`) — these should be migrated to `_single_underscore` convention
- `MediaListEntry.update_list_entry` calls `self.media_id` but `MediaListEntry` only inherits from `ListEntry`, not `Media`, so the field doesn't exist — needs either `media_id: int = Field(alias="mediaId")` added directly to `MediaListEntry`, or a decision to make it extend `Media` too
