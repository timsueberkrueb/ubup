# -*- coding: utf-8 -*-

from . import termcol


def _print_colorized(*values, color, sep: str=' ', end: str='\n'):
    print(color + sep.join(values), termcol.COLORS.ENDC, sep='', end=end)


def success(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=termcol.COLORS.SUCCESS, sep=sep, end=end)


def header(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=termcol.COLORS.HEADER, sep=sep, end=end)


def information(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=termcol.COLORS.INFORMATION, sep=sep, end=end)


def warning(*values, sep: str=' ', end: str='\n'):
    _print_colorized(*values, color=termcol.COLORS.WARNING, sep=sep, end=end)
