from pathlib import Path


def _load(name: str) -> str:
    return (Path(__file__).parent / "queries" / name).read_text()


get_user = _load("get_user.graphql")
get_media = _load("get_media.graphql")
get_expanded_media_info = _load("get_expanded_media_info.graphql")
update_entry = _load("update_entry.graphql")
get_media_list = _load("get_media_list.graphql")
