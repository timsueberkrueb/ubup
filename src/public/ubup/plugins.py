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

    def __init__(self, config=None, data_path: str=None):
        """
        :param config: Plugin configuration
        :param data_path: Path to configuration folder
        """
        self.config = config
        self.data_path = data_path

    @staticmethod
    def run_command(command: str, *args, log_command: bool=True):
        """
        Run a command
        :param command: Command to run
        :param args: Command arguments
        :param log_command: Whether to log the command to the console
        """
        if log_command:
            print('$', command, *args)
        subprocess.check_call([command, *args])

    @staticmethod
    def run_command_sudo(command: str, *args, log_command: bool=True):
        """
        Run a command with sudo
        :param command: Command to run
        :param args: Command arguments
        :param log_command: Whether to log the command to the console
        """
        AbstractPlugin.run_command('sudo', command, *args, log_command=log_command)

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
            path = f'{self.data_path}/{path}'
        return path
