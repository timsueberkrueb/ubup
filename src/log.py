# -*- coding: utf-8 -*-

from . import termcol


def header(*values, sep: str=' ', end: str='\n', bold: bool=False, underline: bool=False):
    print(termcol.header(sep.join(values), bold=bold, underline=underline), end=end)


def information(*values, sep: str=' ', end: str='\n', bold: bool=False, underline: bool=False):
    print(termcol.information(sep.join(values), bold=bold, underline=underline), end=end)


def success(*values, sep: str=' ', end: str='\n', bold: bool=False, underline: bool=False):
    print(termcol.success(sep.join(values), bold=bold, underline=underline), end=end)


def warning(*values, sep: str=' ', end: str='\n', bold: bool=False, underline: bool=False):
    print(termcol.warning(sep.join(values), bold=bold, underline=underline), end=end)


def error(*values, sep: str=' ', end: str='\n', bold: bool=False, underline: bool=False):
    print(termcol.error(sep.join(values), bold=bold, underline=underline), end=end)


def regular(*values, sep: str=' ', end: str='\n', bold: bool=False, underline: bool=False):
    print(termcol.regular(sep.join(values), bold=bold, underline=underline), end=end)

