#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time

import click


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.dirname(TESTS_DIR)


SUPPORTED_UBUNTU_RELEASES = (
    'xenial',    # 16.04
    'artful',    # 17.10
)


def _check_is_lxc_installed():
    try:
        subprocess.check_call(['lxd', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call(['lxc', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise click.ClickException('LXD doesn\'t seem to be installed on your system or is not in $PATH.\n'
                                   'LXD is required to run tests without polluting the host system.\n'
                                   'Install it by running:\n'
                                   '$ snap install lxd\n'
                                   'and set it up by running:\n'
                                   '$ lxd init')


def _wait_for_network(container_name):
    print('Waiting for a network connection ...')
    connected = False
    retry_count = 25
    network_probe = 'import urllib.request; urllib.request.urlopen("{}", timeout=5)' \
        .format('http://start.ubuntu.com/connectivity-check.html')
    while not connected:
        time.sleep(1)
        try:
            result = subprocess.check_call(
                ['lxc', 'exec', container_name, '--',
                 'python3', '-c', "'" + network_probe + "'"]
            )
            connected = result == 0
        except subprocess.CalledProcessError:
            connected = False
            retry_count -= 1
            if retry_count == 0:
                raise ConnectionError("No network connection")
    print('Network connection established')


def _run_in_lxc_container(verbose: bool=False):
    for release in SUPPORTED_UBUNTU_RELEASES:
        run_tests_command = ['bash', '-c', 'cd /root/ubup '
                                           '&& python3 ./tests/run_tests.py --perform-on-host'
                                           + ' --verbose' if verbose else '']
        container_image = 'ubuntu:{}'.format(release)
        container_name = 'ubup-tests-runner-{}'.format(release)
        subprocess.check_call(['lxc', 'launch', '-e', container_image, container_name])
        try:
            # Push the source code to the container
            subprocess.check_call(['lxc', 'file', 'push', '-r', SOURCE_ROOT, container_name + '/root'])
            _wait_for_network(container_name)
            # Update and upgrade our fresh container
            subprocess.check_call(['lxc', 'exec', container_name, '--', 'apt-get', 'update'])
            subprocess.check_call(['lxc', 'exec', container_name, '--', 'apt-get', '-y', 'upgrade'])
            # Install Python and pip
            subprocess.check_call(['lxc', 'exec', container_name, '--',
                                   'apt-get', '-y', 'install', 'python3', 'python3-pip'])
            # Install ubup dependencies
            subprocess.check_call(['lxc', 'exec', container_name, '--',
                                   'pip3', 'install', 'click', 'ruamel.yaml', 'schema', 'progressbar2'])
            # Install squashfs (required for snaps to work)
            subprocess.check_call(['lxc', 'exec', container_name, '--',
                                   'apt-get', 'install', 'squashfuse'])
            # Install test requirements
            subprocess.check_call(['lxc', 'exec', container_name, '--', 'pip3', 'install', 'pytest'])
            # Run the test suite in the container
            subprocess.check_call(['lxc', 'exec', container_name, '--', *run_tests_command])
            # Delete the container
            subprocess.check_call(['lxc', 'delete', '-f', container_name])
        except subprocess.CalledProcessError as e:
            print('An error occurred, trying to destroy container ...')
            subprocess.check_call(['lxc', 'delete', '-f', container_name])
            print('Container destroyed.')
            raise e


def _run_on_host(verbose: bool=False):
    env = os.environ
    env['PYTHONPATH'] = SOURCE_ROOT
    cmd = ['pytest']
    if verbose:
        cmd += ['--verbose', '--capture=no']
    subprocess.check_call(cmd, cwd=TESTS_DIR, env=env)


@click.command()
@click.option('--verbose', default=False, is_flag=True, help='Enable verbose output.')
@click.option('--perform-on-host', default=False, is_flag=True,
              help='Perform tests on the host rather than inside of a container. '
                   'You should not invoke this manually.')
def main(verbose: bool=False, perform_on_host: bool=False):
    if perform_on_host:
        _run_on_host(verbose)
    else:
        _check_is_lxc_installed()
        _run_in_lxc_container(verbose)


if __name__ == '__main__':
    main()
