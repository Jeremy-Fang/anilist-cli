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

- **`AnilistAPI`** — raw async HTTP client wrapping the AniList GraphQL API
- **`GraphQLAdapter`** — translates between Python objects (filters, models) and GraphQL query strings/variables
- **Models** — Pydantic models organized in an inheritance hierarchy: `Media` + `ListEntry` → `CompleteDocument` → `Anime` / `Manga`; `MediaPreview` → `AnimePreview` / `MangaPreview`

## Caching

Responses are cached in a local SQLite database (`query_cache.db`) keyed by `(query, variables, user)`. Cache entries expire after a TTL and are also invalidated by a version counter (`_v` on `AnilistAPI`) that must be incremented after every mutation via `authenticated_call`. Failing to increment `_v` after a write will cause the cache to serve stale data.

The SQLite cache was chosen as a learning exercise — an in-memory dict or a TTL cache (`cachetools`, `aiocache`) would also work for a short-lived CLI process.

## Tooling Notes

Uses `uv` for dependency management (replaces Poetry). `uv sync` auto-creates `.venv` in the project root using Python 3.13. Pyright is configured to find it via `venvPath = "."` and `venv = ".venv"` in `pyproject.toml`.

## Testing

Unit tests use manual mocks (inline Python dicts) rather than VCR/recorded cassettes. VCR was ruled out because stale cassettes silently pass against outdated API responses when AniList changes a response shape — catching that requires extra infrastructure (scheduled live runs) not worth adding at this stage. Integration tests are deferred until the feature set stabilizes; when added, they should use real read-only API calls with a test account token in GitHub secrets rather than cassettes.

## Open UML Design Questions (no decisions made yet)

- **`CompleteDocument` and `MediaPreview` inheriting from `ListEntry`** — conflates media identity with user list interaction. A logged-out user has `Media` data but no `ListEntry` data; modeling this as inheritance means all `ListEntry` fields are `None` noise on the object for non-logged-in users. Composition may be more accurate: `CompleteDocument` extends only `Media` and carries `list_entry: ListEntry | None`. This also matches the AniList API response shape (media with an optional nested `mediaListEntry`). No decision made.
- **`MediaListEntry` not inheriting from `Media`** — every other concrete class with media data (`Anime`, `Manga`, `MediaPreview`, `AnimePreview`, `MangaPreview`) inherits from `Media`. `MediaListEntry` defines `id` and `title` directly instead, which is structurally inconsistent and is the root of the known `media_id` bug. No decision made.
- **`AnimePreview` / `MangaPreview` as empty subclasses** — neither adds fields or methods over `MediaPreview`. The only value is distinct types for isinstance checks. Consider whether a single `MediaPreview` with a `media_type` field would be simpler, or whether anime/manga-specific preview fields are planned. No decision made.
- **`notes` vs `note` naming** — `ListEntry` has `notes` (plural), `ListEntryChanges` has `note` (singular). These represent the same concept and should be consistent. No decision made.
- **`adapter: Any` typing on `ListEntry`** — the most critical dependency in the model layer bypasses all type checking. Should be typed against a Protocol after the `AnilistClient` / `AnilistService` refactor. No decision made.
- **`ListEntry → AnilistAPI` connection in UML** — should be removed from the diagram once the service layer refactor is done, since models will no longer hold an API reference.

## Known Gotchas

- `RuntimeState` (not yet implemented) must NOT declare `session_cache` as a direct attribute — access it via `anilist_session.cache` instead. The UML diagram shows both, but the direct attribute is redundant and risks two paths to the same object being used inconsistently
- `ListEntry` currently holds `api: AnilistAPI` so models can call `update_media_entry()` on themselves (Active Record pattern). This creates a circular dependency and couples models to the network layer. Deferred refactor: move `update_media_entry()` and `add_change()` to `GraphQLAdapter` (Service Layer pattern) and make models pure data. This is the industry-standard approach for API clients and CLI tools, and fits the existing three-layer architecture naturally. As part of this refactor, rename `GraphQLAdapter` → `AnilistService` and `AnilistAPI` → `AnilistClient`. "Adapter" undersells the service layer responsibility; "GraphQL" exposes an implementation detail the caller shouldn't know about; and `AnilistAPI` implies it is the API rather than a client wrapping it. The resulting hierarchy reads cleanly: `AnilistClient` (raw HTTP) → `AnilistService` (business logic) → Models (pure data)

- `_v` must be incremented in `authenticated_call` after every successful mutation — this is not yet implemented and is a known bug
- Private helper methods currently use `__dunder__` naming (e.g. `__check_cache__`) — these should be migrated to `_single_underscore` convention
- `MediaListEntry.update_list_entry` calls `self.media_id` but `MediaListEntry` only inherits from `ListEntry`, not `Media`, so the field doesn't exist — needs either `media_id: int = Field(alias="mediaId")` added directly to `MediaListEntry`, or a decision to make it extend `Media` too
