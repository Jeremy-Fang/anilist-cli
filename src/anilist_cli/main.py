import logging

from anilist_cli.ui.app import AnilistApp

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    filemode="a",
    format="%(asctime)s : %(name)s : %(levelname)s : %(message)s",
)


def main() -> None:
    AnilistApp().run()


if __name__ == "__main__":
    main()
