from .libs.anilist.models.filter import *
from .libs.anilist.models.enums import *

from .libs.anilist.anilist import AnilistAPI

from .libs.anilist.graphql_adapter import GraphQLAdapter

from .libs.anilist.queries import *

from .libs.anilist.models.list_entry_changes import ListEntryChanges

import asyncio

import logging

from datetime import date

from .utils.common import *

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
        # user = await api.login(ACCESS_TOKEN)

        # print(user)

        adapter = GraphQLAdapter(api)

        # try:
        #     trending_anime = await adapter.get_trending_media(MediaType.ANIME)
        #     trending_manga = await adapter.get_trending_media(MediaType.MANGA)
        #     all_time_anime = await adapter.get_all_time_media(MediaType.ANIME)
        #     all_time_manga = await adapter.get_all_time_media(MediaType.MANGA)

        #     for entry in trending_anime[:5]:
        #         print(entry)
        # except Exception as e:
        #     print(e)
        # print("1----")

        # upcoming_manga = await adapter.get_upcoming_media(MediaType.MANGA)

        # for entry in all_time_manga[:5]:
        #     print(entry)

        # anime_0 = await all_time_manga[0].get_info()

        # print("media_info", anime_0)

        # print("2----")

        # seasonal_anime = await adapter.get_seasonal_media(MediaType.ANIME)

        # for i, entry in enumerate(seasonal_anime[:5]):
        #     print(i, entry)
        #     print(i, "-------------------------------------------")

        # print("media_info", await seasonal_anime[0].get_info())

        # media_filter = MediaFilter()
        # media_filter["search_string"] = "re:zero"

        # results = (await adapter.search(media_filter))[0]

        # print("3------")

        # for result in results:
        #     print(result)

        # print("4-----")

        media_lists = await adapter.get_media_list(
            "JeremyFang022",
            MediaType.ANIME,
            [MediaListStatus.CURRENT, MediaListStatus.COMPLETED],
        )

        for i, li in enumerate(media_lists):
            print(i, li)

    except Exception as e:
        print(e)
        logger.error(e)

    await api.close()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
