# -*- coding: utf-8 -*-


class _COLORS:
    HEADER = '\033[95m'
    INFORMATION = '\033[94m'
    SUCCESS = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def _print_colorized(*values, color, sep: str=' ', end: str='\n'):
    print(color + sep.join(values), _COLORS.ENDC, sep='', end=end)


def bold(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=_COLORS.BOLD, sep=sep, end=end)


def success(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=_COLORS.SUCCESS, sep=sep, end=end)


def header(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=_COLORS.HEADER, sep=sep, end=end)


def information(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=_COLORS.INFORMATION, sep=sep, end=end)


def warning(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=_COLORS.WARNING, sep=sep, end=end)
