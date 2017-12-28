# -*- coding: utf-8 -*-

import os
import click

from src import config


@click.command()
@click.argument('data_path', default=os.getcwd(), type=click.Path(exists=True, file_okay=False))
def main(data_path: str):
    setup_filename = os.path.join(data_path, 'setup.yaml')

    if not os.path.isfile(setup_filename):
        raise click.ClickException('The file {} does not exist'.format(setup_filename))

    setup = config.Setup(data_path)
    setup.load_plugins()
    setup.load_config(setup_filename)

    setup.perform()


if __name__ == '__main__':
    main()
