#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import tempfile

import click


TESTS_DIR = os.path.abspath(os.path.dirname(__file__))
SOURCE_ROOT = os.path.dirname(TESTS_DIR)


SUPPORTED_UBUNTU_RELEASES = (
    'xenial',    # 16.04
    'artful',    # 17.10
)


_CONTAINER_ENGINE_MISSING_MESSAGE = '''LXD or Docker are required in order to run tests without polluting the host system.
Switch between container engines using the --docker or --lxd command line options.
Install LXD it by running:
$ snap install lxd
and set it up by running:
$ lxd init
Install Docker by running:
$ snap install docker
'''


def _check_is_lxd_installed():
    try:
        subprocess.check_call(['lxd', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise click.ClickException('LXD doesn\'t seem to be installed on your system or is not in $PATH.\n'
                                   + _CONTAINER_ENGINE_MISSING_MESSAGE)


def _check_is_docker_installed():
    try:
        subprocess.check_call(['docker', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise click.ClickException('Docker doesn\'t seem to be installed on your system or is not in $PATH.\n'
                                   + _CONTAINER_ENGINE_MISSING_MESSAGE)


def _docker_wait_for_snapd(container_name):
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


def _run_with_docker(verbose: bool=False):
    for release in SUPPORTED_UBUNTU_RELEASES:
        run_tests_command = ['bash', '-c', 'export LC_ALL=C.UTF-8 && export LANG=C.UTF-8 '
                                           '&& cd /root/ubup '
                                           '&& python3 ./tests/run_tests.py --perform-on-host'
                                           + (' --verbose' if verbose else '')]
        container_name = 'ubup-tests-runner-{}'.format(release)

        # Source: https://github.com/ogra1/snapd-docker
        subprocess.check_call([
            'docker', 'run', '--name={}'.format(container_name), '-it', '--tmpfs', '/run', '--tmpfs', '/run/lock',
            '--tmpfs', '/tmp', '--cap-add', 'SYS_ADMIN', '--device=/dev/fuse', '--security-opt', 'apparmor:unconfined',
            '--security-opt', 'seccomp:unconfined', '-v', '/sys/fs/cgroup:/sys/fs/cgroup:ro',
            '-v', '/lib/modules:/lib/modules:ro', '-d', 'ubup-snapd-ubuntu-{}'.format(release)
        ])
        subprocess.check_call(['docker', 'start', container_name])

        try:
            # Wait for snapd to start up
            _docker_wait_for_snapd(container_name)
            # Edge core snap currently required
            subprocess.check_call(['docker', 'exec', '-i', container_name, 'snap', 'install', 'core', '--edge'])
            # Push the source code to the container
            subprocess.check_call(['docker', 'cp', SOURCE_ROOT, container_name + ':/root'])
            # Update and upgrade our fresh container
            subprocess.check_call(['docker', 'exec', '-i', container_name, 'apt-get', 'update'])
            subprocess.check_call(['docker', 'exec', '-i', container_name, 'apt-get', '-y', 'upgrade'])
            # Install software-properties-common (for add-apt-repository)
            # which is not installed by default in the Ubuntu Docker images.
            subprocess.check_call(['docker', 'exec', '-i', container_name,
                                   'apt-get', '-y', 'install', 'software-properties-common'])
            # Install Python and pip
            subprocess.check_call(['docker', 'exec', '-i', container_name,
                                   'apt-get', '-y', 'install', 'python3', 'python3-pip'])
            # Install ubup dependencies
            subprocess.check_call(['docker', 'exec', '-i', container_name,
                                   'pip3', 'install', 'click', 'ruamel.yaml', 'schema', 'progressbar2'])
            # Install test requirements
            subprocess.check_call(['docker', 'exec', '-i', container_name, 'pip3', 'install', 'pytest'])
            # Run the test suite in the container
            subprocess.check_call(['docker', 'exec', '-i', container_name, *run_tests_command])
            # Delete the container
            subprocess.check_call(['docker', 'rm', '-f', container_name])
        except subprocess.CalledProcessError as e:
            print('An error occurred, trying to destroy container ...')
            subprocess.check_call(['docker', 'rm', '-f', container_name])
            print('Container destroyed.')
            raise e


def _build_docker_images():
    dockerfile_in = os.path.join(TESTS_DIR, 'docker', 'Dockerfile.in')
    with open(dockerfile_in) as file:
        dockerfile_text = file.read()
    for release in SUPPORTED_UBUNTU_RELEASES:
        with tempfile.TemporaryDirectory() as tempdir:
            with open(os.path.join(tempdir, 'Dockerfile'), 'w') as file:
                file.write(dockerfile_text.replace('$RELEASE', release))
            subprocess.check_call(['docker', 'build', '-t', 'ubup-snapd-ubuntu-{}'.format(release), '.'],
                                  cwd=os.path.join(tempdir))


def _lxc_wait_for_network(container_name):
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


def _run_with_lxd(verbose: bool=False):
    for release in SUPPORTED_UBUNTU_RELEASES:
        run_tests_command = ['bash', '-c', 'export LC_ALL=C.UTF-8 && export LANG=C.UTF-8 '
                                           '&& cd /root/ubup '
                                           '&& python3 ./tests/run_tests.py --perform-on-host'
                                           + (' --verbose' if verbose else '')]
        container_image = 'ubuntu:{}'.format(release)
        container_name = 'ubup-tests-runner-{}'.format(release)
        subprocess.check_call(['lxc', 'launch', '-e', container_image, container_name])
        try:
            # Push the source code to the container
            subprocess.check_call(['lxc', 'file', 'push', '-r', SOURCE_ROOT, container_name + '/root'])
            _lxc_wait_for_network(container_name)
            # Update and upgrade our fresh container
            subprocess.check_call(['lxc', 'exec', container_name, '--', 'apt-get', 'update'])
            subprocess.check_call(['lxc', 'exec', container_name, '--', 'apt-get', '-y', 'upgrade'])
            # Install squashfs (required for snaps to work)
            subprocess.check_call(['lxc', 'exec', container_name, '--',
                                   'apt-get', '-y', 'install', 'squashfuse'])
            # Install Python and pip
            subprocess.check_call(['lxc', 'exec', container_name, '--',
                                   'apt-get', '-y', 'install', 'python3', 'python3-pip'])
            # Install ubup dependencies
            subprocess.check_call(['lxc', 'exec', container_name, '--',
                                   'pip3', 'install', 'click', 'ruamel.yaml', 'schema', 'progressbar2'])
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
@click.option('--docker/--lxd', default=False, is_flag=True, help='Container engine to use')
@click.option('--build-docker-images', default=False, is_flag=True, help='Build Docker images')
@click.option('--perform-on-host', default=False, is_flag=True,
              help='Perform tests on the host rather than inside of a container. '
                   'You should not invoke this manually.')
def main(verbose: bool=False, docker: bool=False, build_docker_images: bool=False, perform_on_host: bool=False):
    if build_docker_images:
        _check_is_docker_installed()
        _build_docker_images()
    if perform_on_host:
        _run_on_host(verbose)
    elif docker:
        _check_is_docker_installed()
        _run_with_docker(verbose)
    else:
        _check_is_lxd_installed()
        _run_with_lxd(verbose)


if __name__ == '__main__':
    main()
