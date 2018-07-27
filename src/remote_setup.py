# -*- coding: utf-8 -*-

from typing import List, Optional

import sys
import os
import subprocess

from . import log


def perform(setup_filename: str, remote: str):
    if 'UBUP_EXECUTABLE' in os.environ:
        ubup_local_exec_path = os.environ['UBUP_EXECUTABLE']
    elif getattr(sys, 'frozen', False):
        # Running in a bundle created by PyInstaller
        # sys.executable points to the bundle
        ubup_local_exec_path = sys.executable
    else:
        # Running in live mode. sys.executable points
        # to the Python interpreter
        log.error('Remote setup is currently only supported when ubup is running as standalone binary.')
        log.error('For debugging purposes, please consider setting the environment variable '
                  'UBUP_EXECUTABLE to the path of a local ubup executable.')
        sys.exit(1)

    config_dir = os.path.dirname(setup_filename)

    log.information('Checking connection.')
    _probe(remote)

    temp_dir = _ssh_capture(remote, ['mktemp', '-d', '-t', 'ubup.tmp.XXXXXXXXXX']).strip()

    log.information('Copying files.')
    _copy_files(config_dir, remote, temp_dir)

    # Check for an existing ubup installation
    ubup_remote_exec_path = _attempt_find_ubup(remote)
    if ubup_remote_exec_path is not None:
        log.information('ubup is already installed remotely.')
    else:
        log.information('ubup is not installed remotely.')
        log.information('Temporarily installing ubup remotely.')
        _copy_ubup(ubup_local_exec_path, remote, temp_dir)
        ubup_remote_exec_path = os.path.join(temp_dir, 'ubup')

    log.information('Running ubup remotely.')
    _run_ubup(remote, temp_dir, ubup_remote_exec_path)


def _probe(remote: str):
    distro = _ssh_capture(remote, ['lsb_release', '--short', '--id']).strip()
    release = _ssh_capture(remote, ['lsb_release', '--short', '--release']).strip()
    if distro.casefold() != 'ubuntu':
        log.warning('Remote distribution id is {}. '
                    'Only Ubuntu-based GNU/Linux distributions are supported.'.format(distro))
    log.success('Successfully connected to {} ({} {}).'.format(remote, distro, release))


def _copy_files(config_dir: str, remote: str, remote_path: str):
    remote_config_dir = os.path.join(remote_path, 'setup')
    _scp_recursive(remote, config_dir, remote_config_dir)


def _attempt_find_ubup(remote: str) -> Optional[str]:
    try:
        return _ssh_capture(remote, ['which', 'ubup']).strip()
    except subprocess.CalledProcessError:
        return None


def _copy_ubup(ubup_executable_path: str, remote: str, remote_path: str):
    _scp(remote, ubup_executable_path, os.path.join(remote_path, 'ubup'))


def _run_ubup(remote: str, remote_path: str, remote_ubup_executable: str):
    args = _argv_without_args(['-p', '--path', '--remote'])
    _ssh(remote, [remote_ubup_executable, '-p', os.path.join(remote_path, 'setup'), *args])


def _ssh(remote: str, command):
    command_str = ' '.join(command)
    subprocess.check_call(['ssh', remote, '--', command_str])


def _ssh_capture(remote: str, command) -> str:
    command_str = ' '.join(command)
    return _capture_command(['ssh', remote, '--', command_str])


def _scp(remote: str, source: str, dest: str):
    subprocess.check_call(['scp', source, '{}:{}'.format(remote, dest)])


def _scp_recursive(remote: str, source: str, dest: str):
    subprocess.check_call(['scp', '-r', source, '{}:{}'.format(remote, dest)])


def _argv_without_args(args_to_remove: List[str]) -> List[str]:
    args = sys.argv[1:]
    for arg_to_remove in args_to_remove:
        try:
            idx = args.index(arg_to_remove)
            args.pop(idx + 1)
            args.pop(idx)
        except ValueError:
            pass
    return args


def _capture_command(command: List[str]) -> str:
    command_str = ' '.join(command)
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    output = ''
    for line in iter(p.stdout.readline, ''):
        output += line.strip() + '\n'
    p.stdout.close()
    return_code = p.wait()
    if return_code != 0:
        log.error(output)
        raise subprocess.CalledProcessError(return_code, command_str)
    return output
