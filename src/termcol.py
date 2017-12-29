# -*- coding: utf-8 -*-


class COLORS:
    HEADER = '\033[95m'
    INFORMATION = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _colorize(text: str, color) -> str:
    return color + text + COLORS.ENDC


def header(text: str) -> str:
    return _colorize(text, COLORS.HEADER)


def information(text: str) -> str:
    return _colorize(text, COLORS.INFORMATION)


def success(text: str) -> str:
    return _colorize(text, COLORS.SUCCESS)


def warning(text: str) -> str:
    return _colorize(text, COLORS.WARNING)


def error(text: str) -> str:
    return _colorize(text, COLORS.ERROR)


def bold(text: str) -> str:
    return _colorize(text, COLORS.BOLD)


def underline(text: str) -> str:
    return _colorize(text, COLORS.UNDERLINE)
