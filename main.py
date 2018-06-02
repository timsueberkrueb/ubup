#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import click
from src import options
from src import local_setup
from src import remote_setup


@click.group(invoke_without_command=True)
@click.pass_context
@options.setup_options
def cli(ctx: click.Context, **_):
    if ctx.invoked_subcommand is None:
        ctx.forward(setup)


@cli.command('setup')
@options.setup_options
def setup(path: str, no_roots: bool=False, verbose: bool=False, remote: str=None, rerun: bool=False):
    if os.path.isdir(path):
        setup_filename = os.path.join(path, 'setup.yaml')
    else:
        setup_filename = path

    if not os.path.isfile(setup_filename):
        raise click.ClickException('The file {} does not exist.'.format(setup_filename))
    if not setup_filename[setup_filename.rfind('.') + 1:] in ('yaml', 'yml'):
        raise click.ClickException('The file {} has an unsupported extension. '
                                   'Supported extensions are *.yaml and *.yml.'
                                   .format(setup_filename))

    if remote is None:
        local_setup.perform(setup_filename, no_roots, verbose, rerun)
    else:
        remote_setup.perform(setup_filename, remote)


if __name__ == '__main__':
    cli()
