from .libs.anilist.models.filter import *
from .libs.anilist.models.enums import *

from .libs.anilist.anilist import AnilistAPI

from .libs.anilist.graphql_adapter import GraphQLAdapter

from .libs.anilist.queries import *

from .libs.anilist.models.list_entry_changes import ListEntryChanges

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
    api = AnilistAPI()

    try:
        user = await api.login(ACCESS_TOKEN)

        # print(user)

        anilist = GraphQLAdapter(api)

        try:
            trending_anime = await anilist.get_trending_media(MediaType.ANIME)
            trending_manga = await anilist.get_trending_media(MediaType.MANGA)
            all_time_anime = await anilist.get_all_time_media(MediaType.ANIME)
            all_time_manga = await anilist.get_all_time_media(MediaType.MANGA)

            for entry in trending_anime[:5]:
                print(entry)
        except Exception as e:
            print(e)
        print("1----")

        for entry in all_time_anime[:5]:
            print(entry)

        anime_0 = await all_time_anime[0].get_info()

        print("media_info", anime_0)

        anime_0.add_changes("status", MediaListStatus.COMPLETED)

        print(anime_0.changes)
        # print("2----")

        # seasonal_anime = await anilist.get_seasonal_media(MediaType.ANIME)

        # for i, entry in enumerate(seasonal_anime[:5]):
        #     print(i, entry)
        #     print(i, "-------------------------------------------")

        # print("media_info", await seasonal_anime[0].get_info())

        # media_filter = MediaFilter()
        # media_filter["search_string"] = "re:zero"

        # results = await anilist.search(media_filter)

        # print("3------")

        # for result in results:
        #     print(result)

        print("4-----")

        # media_list = await anilist.get_media_list(
        #     "Chikaraa", MediaType.ANIME, [MediaListStatus.CURRENT]
        # )

        # for i, entry in enumerate(media_list):
        #     print(i, entry)

    except Exception as e:
        print(e)
        logger.error(e)

    await api.close()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
