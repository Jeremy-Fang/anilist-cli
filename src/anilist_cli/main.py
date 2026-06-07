import asyncio
import logging

from .libs.anilist.adapter import AnilistAdapter
from .libs.anilist.client import AnilistClient
from .libs.anilist.models.filter import MediaFilter
from .libs.anilist.service import AnilistService

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    filemode="a",
    format="%(asctime)s : %(name)s : %(levelname)s : %(message)s",
)


async def start():
    client = AnilistClient()

    try:
        adapter = AnilistAdapter(client)
        service = AnilistService(adapter)

        media_filter = MediaFilter()
        media_filter["search_string"] = "re:zero"

        results = (await service.search(media_filter))[0]

        print("3------")

        for result in results:
            print(result)

        print("4-----")

    except Exception as e:
        print(e)
        logger.error(e)

    await client.close()


def main():
    asyncio.run(start())


if __name__ == "__main__":
    main()
