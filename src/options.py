# -*- coding: utf-8 -*-

import os
import click


def setup_options(func):
    @click.option('-p', '--path', default=os.getcwd(), type=click.Path(exists=True, resolve_path=True),
                  help='Path to folder or setup.yaml file')
    @click.option('-v', '--verbose', default=False, is_flag=True,
                  help='Enable verbose output. Disables tree-like output.')
    @click.option('--remote', default=None, help='Remote host to connect to via SSH (e.g. hostname or user@hostname)')
    @click.option('--rerun', default=False, is_flag=True, help='Rerun all steps even if they were already run')
    @click.option('--no-roots', default=False, is_flag=True, help='Disable tree-like progress output.')
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
