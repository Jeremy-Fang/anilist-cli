from InquirerPy import inquirer

from typing import List
from typing import Optional
from typing import Any

import os
import platform

all_choices: List[str] = [
    "Java",
    "C",
    "C++",
    "Javascript",
    "Python",
    "Typescript",
    "Ruby",
]


def prompt_with_pages(
    message: str, results: List[str], page_size: Optional[int] = 20
) -> str:
    """
    Wrapper function around InquirerPy select to allow for multi-page prompts

    @type message: str
    @type results: List[str]
    @type page_size: Optional[int]
    @param message: prompt message
    @param results: list of choices
    @param page_size: number of choices per page
    @rtype: str
    @return: string of selected choice
    """
    page: int = 1
    results_length: int = len(results)

    system_platform: str = platform.system()

    prompt: Any = inquirer.select(
        message=message, choices=results[(page - 1) * page_size : page * page_size]
    )

    selected: Optional[str] = None

    while selected is None or selected in ["left", "right"]:
        if system_platform != "":
            if system_platform == "Windows":
                os.system("cls")
            else:
                os.system("clear")

        @prompt.register_kb("left")
        def _get_prev_page(event):
            if page > 1:
                event.app.exit(result="left")

        @prompt.register_kb("right")
        def _get_next_page(event):
            if page * page_size < results_length:
                event.app.exit(result="right")

        selected = prompt.execute()

        if selected == "left":
            page -= 1

        if selected == "right":
            page += 1

        prompt = inquirer.select(
            message=message,
            choices=results[(page - 1) * page_size : page * page_size],
        )

    return selected
