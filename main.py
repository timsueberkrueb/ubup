# -*- coding: utf-8 -*-

import os
import click
import random

from src import config
from src import log


@click.command()
@click.argument('data_path', default=os.getcwd(), type=click.Path(exists=True, file_okay=False))
@click.option('--roots/--no-roots', default=True, help='Enable/disable tree-like progress output.')
def main(data_path: str, roots: bool=True):
    setup_filename = os.path.join(data_path, 'setup.yaml')

    if not os.path.isfile(setup_filename):
        raise click.ClickException('The file {} does not exist'.format(setup_filename))

    if not roots and random.SystemRandom().randrange(0, 100) == 42:
        print('🎶 https://youtu.be/PUdyuKaGQd4 🎶')   # *Totally no easter 🥚*

    log.success('🚀 Performing your setup.', bold=True)

    setup = config.Setup(data_path)
    setup.load_plugins()
    setup.load_config(setup_filename)

    setup.perform(indent=roots)

    log.success('✓ Setup completed.', bold=True)


if __name__ == '__main__':
    main()
