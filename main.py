#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import click
import random

from src import config
from src import log


def _require_root():
    root_mode = 'UBUP_STAGE_1' not in os.environ
    user_mode = 'UBUP_STAGE_1' in os.environ \
                and 'UBUP_STAGE_2' not in os.environ
    if root_mode or user_mode:
        launch_env = os.environ
        if root_mode:
            launch_env['UBUP_STAGE_1'] = '1'
        if user_mode:
            launch_env['UBUP_STAGE_2'] = '1'

        try:
            u = os.environ['SUDO_USER']
        except KeyError:
            u = os.environ['USER']

        args = ['sudo', '-E']
        if user_mode:
            args += ['-u', u]
        args += [sys.executable]

        if getattr(sys, 'frozen', False):
            # Running in a bundle created by PyInstaller
            # sys.executable already points to the bundle
            args += [launch_env]
        else:
            # Running in live mode. sys.executable points
            # to the Python interpreter
            args += sys.argv + [launch_env]

        # Replace the current process
        os.execlpe('sudo', *args)


@click.command()
@click.argument('config_path', default=os.getcwd(), type=click.Path(exists=True, resolve_path=True))
@click.option('-v', '--verbose', default=False, is_flag=True, help='Enable verbose output. Disables tree-like output.')
@click.option('--no-roots', default=False, is_flag=True, help='Disable tree-like progress output.')
def main(config_path: str, no_roots: bool=False, verbose: bool=False):
    _require_root()

    if os.path.isdir(config_path):
        setup_filename = os.path.join(config_path, 'setup.yaml')
    else:
        setup_filename = config_path

    if not os.path.isfile(setup_filename):
        raise click.ClickException('The file {} does not exist.'.format(setup_filename))
    if not setup_filename[setup_filename.rfind('.')+1:] in ('yaml', 'yml'):
        raise click.ClickException('The file {} has an unsupported extension. '
                                   'Supported extensions are *.yaml and *.yml.'
                                   .format(setup_filename))

    config_dir = os.path.dirname(setup_filename)

    if no_roots and random.SystemRandom().randrange(0, 100) == 42:
        print('🎶 https://youtu.be/PUdyuKaGQd4 🎶')   # *Totally no easter 🥚*

    log.success('🚀 Performing your setup.', bold=True)

    setup = config.Setup(config_dir)
    setup.load_plugins()
    setup.load_config_file(setup_filename)

    setup.perform(indent=not (no_roots or verbose), verbose=verbose)

    log.success('✓ Setup completed.', bold=True)


if __name__ == '__main__':
    main()
