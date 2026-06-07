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

Four-layer design:

- **`AnilistClient`** (`libs/anilist/client.py`) — raw async HTTP client wrapping the AniList GraphQL API
- **`AnilistAdapter`** (`libs/anilist/adapter.py`) — translates between Python objects (filters, models) and GraphQL queries/variables; parses raw API responses into model instances
- **`AnilistService`** (`libs/anilist/service.py`) — business logic layer; owns preset queries (trending, seasonal, etc.) and delegates raw operations to `AnilistAdapter`. Screens interact with this layer only.
- **Models** — Pydantic models organized in an inheritance hierarchy: `Media` + `ListEntry` → `CompleteDocument` → `Anime` / `Manga`; `MediaPreview` → `AnimePreview` / `MangaPreview`

GraphQL queries live as static `.graphql` files under `libs/anilist/queries/` and are loaded at import time by `queries.py`. Variables are passed as a plain dict; Pydantic's `model_dump(by_alias=True)` handles the Python snake_case → GraphQL camelCase mapping via `Field(alias=...)` on each model field.

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
│   └── cli_state.py          # screen inventory — delete once all screens are implemented
├── ui/
│   ├── app.py                # Textual App subclass
│   ├── runtime_state.py      # owns AnilistClient, AnilistAdapter, AnilistService, user session
│   └── screens/              # one Screen subclass per view
│       ├── login.py
│       ├── main_menu.py
│       ├── search.py
│       ├── media_info.py
│       └── ...
├── utils/
└── libs/
```

**Remaining refactors before screens are complete:**

- **`CLIState` gets deleted.** Textual tracks the screen stack natively via `push_screen` / `pop_screen`. Each `CLIState` value becomes a `Screen` subclass; `models/cli_state.py` is kept as a screen inventory reference until all screens are implemented, then removed.
- **`RuntimeState` must own the `AnilistClient` instance and call `close()` on app exit.** Textual runs a single event loop for the entire app lifetime, so the `aiohttp.ClientSession` created inside `AnilistClient.__init__()` naturally lives as long as `RuntimeState` holds the reference — no session injection or parameter changes needed. The only reason to inject the session from outside would be for unit testability (passing a mock session), which is a separate concern.
- **InquirerPy can be removed** once all screens are ported to Textual widgets. `prompt_with_pages` in `inquirer_util.py` becomes a Textual `ListView` or `Select` widget with custom keybindings.

## Open UML Design Questions (no decisions made yet)

- **`CompleteDocument` and `MediaPreview` inheriting from `ListEntry`** — conflates media identity with user list interaction. A logged-out user has `Media` data but no `ListEntry` data; modeling this as inheritance means all `ListEntry` fields are `None` noise on the object for non-logged-in users. Composition may be more accurate: `CompleteDocument` extends only `Media` and carries `list_entry: ListEntry | None`. This also matches the AniList API response shape (media with an optional nested `mediaListEntry`). No decision made.
- **`MediaListEntry` not inheriting from `Media`** — every other concrete class with media data (`Anime`, `Manga`, `MediaPreview`, `AnimePreview`, `MangaPreview`) inherits from `Media`. `MediaListEntry` defines `id`, `media_id`, and `title` directly instead, which is structurally inconsistent. (`media_id` was fixed by adding `Field(alias="mediaId")` directly, but the inheritance inconsistency remains.) No decision made.
- **`AnimePreview` / `MangaPreview` as empty subclasses** — neither adds fields or methods over `MediaPreview`. The only value is distinct types for isinstance checks. Consider whether a single `MediaPreview` with a `media_type` field would be simpler, or whether anime/manga-specific preview fields are planned. No decision made.
- **`notes` vs `note` naming** — `ListEntry` has `notes` (plural), `ListEntryChanges` has `note` (singular). These represent the same concept and should be consistent. No decision made.
- **`adapter: Any` typing on `ListEntry`** — the most critical dependency in the model layer bypasses all type checking. Should be typed against a Protocol after the Active Record pattern is removed. No decision made.

## Known Gotchas

- `RuntimeState` (not yet implemented) must NOT declare `session_cache` as a direct attribute — access it via `anilist_session.cache` instead. The UML diagram shows both, but the direct attribute is redundant and risks two paths to the same object being used inconsistently.

- `ListEntry` currently holds `adapter: AnilistAdapter` so models can call `update_list_entry()` on themselves (Active Record pattern). This creates a circular dependency and couples models to the network layer. Deferred refactor: move `update_list_entry()` and `add_changes()` to `AnilistService` and make models pure data. The resulting hierarchy reads cleanly: `AnilistClient` (raw HTTP) → `AnilistAdapter` (parsing) → `AnilistService` (business logic) → Models (pure data).

- Several deferred DRY/maintainability cleanups remain in `adapter.py` — low priority since they don't affect correctness:
  - `search` iterates `data` twice (transform then construct) — merge into one loop
  - `__dict_enums_to_strs__` builds a list with a `for` loop + `.copy()` — replace with a list comprehension
  - `update_list_entry` repeats a rename-then-delete key pattern three times — collapse with `data.pop()`
  - `update_list_entry` uses `type(data[key]) is dict` — should be `isinstance` for consistency and subclass correctness
  - Explicit `return None` at the end of `__dict_enums_to_strs__`, `__dict_dates_to_fuzzy__`, `__parse_media_list_entry__` — redundant, Python returns `None` implicitly

- **Future migration: `ariadne-codegen`** — generates fully-typed Python client code from `.graphql` files and the AniList schema. Would replace `AnilistAdapter`'s hand-written parsing, `model_dump(by_alias=True)` variable mapping, and the `Field(alias=...)` workarounds. Worth tracking once the feature set stabilises.
