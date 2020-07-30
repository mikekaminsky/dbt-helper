from typing import Dict

import colorama

COLORS: Dict[str, str] = {
    "red": colorama.Fore.RED,
    "green": colorama.Fore.GREEN,
    "yellow": colorama.Fore.YELLOW,
    "reset_all": colorama.Style.RESET_ALL,
}

COLOR_FG_RED = COLORS["red"]
COLOR_FG_GREEN = COLORS["green"]
COLOR_FG_YELLOW = COLORS["yellow"]
COLOR_RESET_ALL = COLORS["reset_all"]


def color(text: str, color_code: str):
    return "{}{}{}".format(color_code, text, COLOR_RESET_ALL)


def green(text: str):
    return color(text, COLOR_FG_GREEN)


def yellow(text: str):
    return color(text, COLOR_FG_YELLOW)


def red(text: str):
    return color(text, COLOR_FG_RED)
