# -*- coding: utf-8 -*-

import os
import click
import random

from src import config
from src import log


@click.command()
@click.argument('data_path', default=os.getcwd(), type=click.Path(exists=True, file_okay=False))
@click.option('-v', '--verbose', default=False, is_flag=True, help='Enable verbose output. Disables tree-like output.')
@click.option('--no-roots', default=False, is_flag=True, help='Disable tree-like progress output.')
def main(data_path: str, no_roots: bool=False, verbose: bool=False):
    setup_filename = os.path.join(data_path, 'setup.yaml')

    if not os.path.isfile(setup_filename):
        raise click.ClickException('The file {} does not exist'.format(setup_filename))

    if no_roots and random.SystemRandom().randrange(0, 100) == 42:
        print('🎶 https://youtu.be/PUdyuKaGQd4 🎶')   # *Totally no easter 🥚*

    log.success('🚀 Performing your setup.', bold=True)

    setup = config.Setup(data_path)
    setup.load_plugins()
    setup.load_config(setup_filename)

    setup.perform(indent=not (no_roots or verbose), verbose=verbose)

    log.success('✓ Setup completed.', bold=True)


if __name__ == '__main__':
    main()
