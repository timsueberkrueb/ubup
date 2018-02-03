#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess
import time

import click


_CONTAINER_ENGINE_MISSING_MESSAGE = '''LXD or Docker are required in order to run tests without polluting the host system.
Switch between container engines using the --docker or --lxd command line options.
Install LXD it by running:
$ snap install lxd
and set it up by running:
$ lxd init
Install Docker by running:
$ snap install docker
'''


def check_is_docker_installed():
    try:
        subprocess.check_call(['docker', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise click.ClickException('Docker doesn\'t seem to be installed on your system or is not in $PATH.')


def check_is_lxd_installed():
    try:
        subprocess.check_call(['lxd', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise click.ClickException('LXD doesn\'t seem to be installed on your system or is not in $PATH.')


def docker_wait_for_snapd(container_name):
    print('Waiting for snapd to start up ...')
    ready = False
    retry_count = 25
    probe = ['docker', 'exec', container_name, 'pgrep', 'snapd']
    while not ready:
        time.sleep(1)
        try:
            result = subprocess.check_call(probe)
            ready = result == 0
        except subprocess.CalledProcessError:
            ready = False
            retry_count -= 1
            if retry_count == 0:
                raise ConnectionError("Error: snapd not running.")
    print('Snapd is up and running.')


def lxd_wait_for_network(container_name):
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
