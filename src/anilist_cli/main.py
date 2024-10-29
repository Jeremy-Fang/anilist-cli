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

ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6ImYyYzgwNzI3MGJhMjcyOGNjNjFmMGIzMDJhNmFmZmE3NzI0NjUxZTFiOWZmYzdmNWFmYWZkOGM2ZjZjOWE0Y2RiNGZlMjM1NWJhYmY1MDYyIn0.eyJhdWQiOiIyMTg3MiIsImp0aSI6ImYyYzgwNzI3MGJhMjcyOGNjNjFmMGIzMDJhNmFmZmE3NzI0NjUxZTFiOWZmYzdmNWFmYWZkOGM2ZjZjOWE0Y2RiNGZlMjM1NWJhYmY1MDYyIiwiaWF0IjoxNzMwMDg2Njk4LCJuYmYiOjE3MzAwODY2OTgsImV4cCI6MTc2MTYyMjY5OCwic3ViIjoiMjczMTI5Iiwic2NvcGVzIjpbXX0.IG3J3SYVUMim1vIxcsZdXnd7KQkwnLBctRgs-IlLk1d2JD-baUGVPNJYXvZcbJwTZWYVLouiD44vzdqHy5vIeWBnSFRM9OfsvBd22bUny3mt_Tes3_Tnc6nmSHi0kwbZ7U-n1LTivjVYxSs0Gw5gllYv1_KRomiVTgHUCGk1RiV3ylroAAdS0-xLe-094d_taDwDTrYQZJ6k6mAXvGC-LLtJHNRDI5fKc8umdTCWo-H6a_VwSNgXl6kGes53eRAopo21SHz6P2Kiro0HDvej1T53GKubSUtKl1CQ7K8sxvUc7uqVJBzF61BJXQBbIIasRDigLzxLT-exk-ZSVN42I3EicZg5CrwGFg88aXG4c2tTv4DPFs2qhLtxqvFF5Pb2iXyOmVZ83HAR9uywx7g_mbM9n2wFutdDK-fCVzbai-oxSVj3S7bg6e3WXpVd7UKfDHsu1WCEJDI2YlFYyozwq8GZzbu_YU0Pu8Kr6kOsMJpu7x7-qScMCTOMPvhB90QojadVM48IkX7I02A0r4VbbwfcV6hgDJDPcGhib4owBORmk_AM0o7ECtSsXafiDtgxbaIku7H9Ok5AtmRncNai_iApFFczshOSFsOV-qweJdDVSN8d_vuQz2ccI6tBpNxoP3Hpt_ZDidk5gtyPJnD91u-8pw16IqDFTFoviIMRxVI"


async def start():
    anilist = AnilistAPI()

    try:
        # user = await anilist.login(ACCESS_TOKEN)

        # print(user)

        trending_anime = await anilist.get_trending_media(MediaType.ANIME)
        # trending_manga = await anilist.get_trending_media(MediaType.MANGA)
        # all_time_anime = await anilist.get_all_time_media(MediaType.ANIME)
        # all_time_manga = await anilist.get_all_time_media(MediaType.MANGA)

        # for entry in trending_anime[:5]:
        #     print(entry)

        # for entry in all_time_anime[:5]:
        #     print(entry)

        # seasonal_anime = await anilist.get_seasonal_media(MediaType.ANIME)

        # for entry in seasonal_anime[:5]:
        #     print(entry)
    except Exception as e:
        print(e)
        logger.error(e)

    await anilist.close()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
