# -*- coding: utf-8 -*-

import os
import click


def setup_options(func):
    @click.argument('config_path', default=os.getcwd(), type=click.Path(exists=True, resolve_path=True))
    @click.option('-v', '--verbose', default=False, is_flag=True,
                  help='Enable verbose output. Disables tree-like output.')
    @click.option('--rerun', default=False, is_flag=True, help='Rerun all steps even if they were already run')
    @click.option('--no-roots', default=False, is_flag=True, help='Disable tree-like progress output.')
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
