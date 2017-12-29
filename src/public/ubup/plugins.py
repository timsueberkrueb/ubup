# -*- coding: utf-8 -*-

import abc
import os
import subprocess


class AbstractPlugin(abc.ABC):
    """
    Abstract base class representing a plugin skeleton

    Static class attributes:
        key:        The unique name this plugin
        schema:     Schema of plugin configuration as defined by the "schema" library
    """
    key = ''
    schema = object

    def __init__(self, config=None, data_path: str=None, verbose: bool=False):
        """
        :param config: Plugin configuration
        :param data_path: Path to configuration folder
        :param verbose: Whether verbose output is enabled
        """
        self.config = config
        self.data_path = data_path
        self._verbose = verbose

    def run_command(self, command: str, *args) -> str:
        """
        Run a command
        :param command: Command to run
        :param args: Command arguments
        :return: Command output
        """

        cmd_str = ' '.join([command, *args])

        p = subprocess.Popen(
            [command, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        output = ''
        for line in iter(p.stdout.readline, ''):
            output += line.strip() + '\n'
            if self._verbose:
                print(line.strip())
        p.stdout.close()
        return_code = p.wait()
        if return_code:
            if not self._verbose:
                print(output)
            raise subprocess.CalledProcessError(return_code, cmd_str)
        return output

    def run_command_sudo(self, command: str, *args) -> str:
        """
        Run a command with sudo
        :param command: Command to run
        :param args: Command arguments
        :return: Command output
        """
        return self.run_command('sudo', command, *args)

    @abc.abstractmethod
    def perform(self):
        """
        Perform setup steps
        """
        pass

    def _expand_path(self, path: str) -> str:
        """
        Sanitize a file or folder path and expand a supported set
        of placeholders and environment variables.
        :param path: Path to a file or folder
        :return: Sanitized and expanded path
        """
        # Strip whitespaces
        path = path.strip()
        # Replace ~ with the user's home directory
        if path.startswith('~'):
            path = path.replace('~', os.environ['HOME'], 1)
        # Expand supported environment variables
        envvars = ('HOME', 'USER')
        for var in envvars:
            path = path.replace(var, os.environ[var] if var in os.environ else '')
        # Support paths relative to the data directory
        if not path.startswith('/'):
            path = '{}/{}'.format(self.data_path, path)
        return path
