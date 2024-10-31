from .libs.anilist.models.filter import *
from .libs.anilist.models.enums import *

from .libs.anilist.anilist import AnilistAPI
from .libs.anilist.models.anime_preview import AnimePreview
from .libs.anilist.models.media_title import MediaTitle

from .libs.anilist.graphql_adapter import GraphQLAdapter

from .libs.anilist.queries import *

import asyncio

import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s : %(levelname)s : %(message)s",
)


async def start():
    anilist = AnilistAPI()

    try:
        # user = await anilist.login(ACCESS_TOKEN)

        # print(user)

        adapter = GraphQLAdapter(anilist)

        # trending_anime = await adapter.get_trending_media(MediaType.ANIME)

        trending_anime = await adapter.get_trending_media(MediaType.ANIME)
        trending_manga = await adapter.get_trending_media(MediaType.MANGA)
        all_time_anime = await adapter.get_all_time_media(MediaType.ANIME)
        all_time_manga = await adapter.get_all_time_media(MediaType.MANGA)

        for entry in trending_anime[:5]:
            print(entry)

        # anime = trending_anime[0]
        # print(anime)

        # anime["title"] = MediaTitle(**anime["title"])
        # anime["status"] = MediaStatus[anime["status"]]
        # anime["format"] = MediaFormat[anime["format"]]
        # anime["api"] = anilist

        # del anime["chapters"]
        # del anime["episodes"]

        # print(AnimePreview.__init__.__code__.co_varnames)
        # anime_preview = AnimePreview(**anime)

        # print(anime_preview)
        # print(anime_preview.popularity)

        print("1----")

        for entry in all_time_anime[:5]:
            print(entry)

        print("2----")

        seasonal_anime = await adapter.get_seasonal_media(MediaType.ANIME)

        for entry in seasonal_anime[:5]:
            print(entry)

        media_info = await adapter.get_media_info(1)

        print("media_info", media_info)

        media_filter = MediaFilter()
        media_filter["search_string"] = "re:zero"

        results = await adapter.search(media_filter)

        print("3------")

        for result in results:
            print(result)

        print("4-----")

        media_list = await adapter.get_media_list(
            "Chikaraa", MediaType.ANIME, [MediaListStatus.CURRENT]
        )

        for i, entry in enumerate(media_list):
            print(i, entry)

    except Exception as e:
        print(e)
        logger.error(e)

    await anilist.close()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
