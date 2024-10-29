from .libs.anilist.models.media_type import MediaType

from .libs.anilist.anilist import AnilistAPI

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

        trending_anime = await anilist.get_trending_media(MediaType.ANIME)
        trending_manga = await anilist.get_trending_media(MediaType.MANGA)
        all_time_anime = await anilist.get_all_time_media(MediaType.ANIME)
        all_time_manga = await anilist.get_all_time_media(MediaType.MANGA)

        for entry in trending_anime[:5]:
            print(entry)

        print("----")

        for entry in all_time_anime[:5]:
            print(entry)

        print("----")

        seasonal_anime = await anilist.get_seasonal_media(MediaType.ANIME)

        for entry in seasonal_anime[:5]:
            print(entry)

    except Exception as e:
        print(e)
        logger.error(e)

    await anilist.close()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
