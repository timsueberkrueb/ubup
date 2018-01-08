# -*- coding: utf-8 -*-

import os
import click
import random

from src import config
from src import log


@click.command()
@click.argument('config_path', default=os.getcwd(), type=click.Path(exists=True, resolve_path=True))
@click.option('-v', '--verbose', default=False, is_flag=True, help='Enable verbose output. Disables tree-like output.')
@click.option('--no-roots', default=False, is_flag=True, help='Disable tree-like progress output.')
def main(config_path: str, no_roots: bool=False, verbose: bool=False):
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
    setup.load_config(setup_filename)

    setup.perform(indent=not (no_roots or verbose), verbose=verbose)

    log.success('✓ Setup completed.', bold=True)


if __name__ == '__main__':
    main()
