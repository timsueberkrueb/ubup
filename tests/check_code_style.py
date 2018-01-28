#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pycodestyle


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.dirname(TESTS_DIR)


def main():
    """
    This tool is using PyCodeStyle (https://github.com/PyCQA/pycodestyle)
    to check the code against the Python Code Style conventions.
    The only exception from the recommended options is the line length
    which is set to 120 instead of the default 79.
    """
    print('Checking code style ...')
    report = pycodestyle.StyleGuide(
        max_line_length=120
    ).check_files("..")
    print('Done.')
    if report.get_count() > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
