# -*- coding: utf-8 -*-


class COLORS:
    DEFAULT = ''
    HEADER = '\033[95m'
    INFORMATION = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _colorize(text: str, color, bold: bool=False, underline: bool=False) -> str:
    if bold:
        color += COLORS.BOLD
    if underline:
        color += COLORS.UNDERLINE
    return color + text + COLORS.ENDC


def header(text: str, bold: bool=False, underline: bool=False) -> str:
    return _colorize(text, COLORS.HEADER, bold=bold, underline=underline)


def information(text: str, bold: bool=False, underline: bool=False) -> str:
    return _colorize(text, COLORS.INFORMATION, bold=bold, underline=underline)


def success(text: str, bold: bool=False, underline: bool=False) -> str:
    return _colorize(text, COLORS.SUCCESS, bold=bold, underline=underline)


def warning(text: str, bold: bool=False, underline: bool=False) -> str:
    return _colorize(text, COLORS.WARNING, bold=bold, underline=underline)


def error(text: str, bold: bool=False, underline: bool=False) -> str:
    return _colorize(text, COLORS.ERROR, bold=bold, underline=underline)

def regular(text: str, bold: bool=False, underline: bool=False) -> str:
    return _colorize(text, COLORS.DEFAULT, bold=bold, underline=underline)
