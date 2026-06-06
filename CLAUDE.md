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

## Known Gotchas

- `_v` must be incremented in `authenticated_call` after every successful mutation — this is not yet implemented and is a known bug
- Private helper methods currently use `__dunder__` naming (e.g. `__check_cache__`) — these should be migrated to `_single_underscore` convention
- `MediaListEntry.update_list_entry` calls `self.media_id` but `MediaListEntry` only inherits from `ListEntry`, not `Media`, so the field doesn't exist — needs either `media_id: int = Field(alias="mediaId")` added directly to `MediaListEntry`, or a decision to make it extend `Media` too
