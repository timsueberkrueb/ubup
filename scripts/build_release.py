#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess

import click

import container_utils


SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

UBUNTU_RELEASE = 'xenial'  # 16.04
RELEASE_ARCH = 'x86_64'


def _build_release(release_version: str):
    container_image = 'ubuntu:{}'.format(UBUNTU_RELEASE)
    container_name = 'ubup-release-builder-{}'.format(UBUNTU_RELEASE)
    subprocess.check_call(['lxc', 'launch', '-e', container_image, container_name])
    try:
        # Push the source code to the container
        subprocess.check_call(['lxc', 'file', 'push', '-r', SOURCE_ROOT, container_name + '/root'])
        container_utils.lxd_wait_for_network(container_name)
        # Update and upgrade our fresh container
        subprocess.check_call(['lxc', 'exec', container_name, '--', 'apt-get', 'update'])
        subprocess.check_call(['lxc', 'exec', container_name, '--', 'apt-get', '-y', 'upgrade'])
        # Install squashfs (required for snaps to work)
        subprocess.check_call(['lxc', 'exec', container_name, '--',
                               'apt-get', '-y', 'install', 'squashfuse'])
        # Install Python and pip
        subprocess.check_call(['lxc', 'exec', container_name, '--',
                               'apt-get', '-y', 'install', 'python3', 'python3-pip'])
        # Install ubup dependencies as well as pyinstaller
        subprocess.check_call(['lxc', 'exec', container_name, '--',
                               'pip3', 'install', 'click', 'ruamel.yaml', 'schema', 'progressbar2', 'pyinstaller',
                               'requests'])
        # Make a release build
        subprocess.check_call(['lxc', 'exec', container_name, '--', 'bash', '-c',
                               'cd /root/ubup && pyinstaller -F -n ubup main.py'])
        # Fetch the release executable
        os.makedirs(os.path.join(SOURCE_ROOT, 'dist'), exist_ok=True)
        subprocess.check_call(['lxc', 'file', 'pull', container_name + '/root/ubup/dist/ubup',
                               os.path.join(SOURCE_ROOT, 'dist', 'ubup-{}-{}-{}'.format(release_version,
                                                                                        UBUNTU_RELEASE,
                                                                                        RELEASE_ARCH))])

        # Delete the container
        subprocess.check_call(['lxc', 'delete', '-f', container_name])
    except subprocess.CalledProcessError as e:
        print('An error occurred, trying to destroy container ...')
        subprocess.check_call(['lxc', 'delete', '-f', container_name])
        print('Container destroyed.')
        raise e


@click.command()
@click.argument('release_version')
def main(release_version: str):
    container_utils.check_is_lxd_installed()
    _build_release(release_version)


if __name__ == '__main__':
    main()
