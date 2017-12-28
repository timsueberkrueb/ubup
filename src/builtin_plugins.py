# -*- coding: utf-8 -*-

import os
import tempfile
import schema

from . import plugins


class AptPackagesPlugin(plugins.AbstractPlugin):
    key = 'apt-packages'
    schema = [str]

    def perform(self):
        packages = self.config
        self.run_command_sudo('apt-get', '-y', '-q', 'install', *packages)


class CreateFoldersPlugin(plugins.AbstractPlugin):
    key = 'folders'
    schema = [str]

    def perform(self):
        folders = self.config
        for folder in folders:
            folder = self._expand_path(folder)
            if not os.path.exists(folder):
                os.mkdir(folder)


class ScriptletsPlugin(plugins.AbstractPlugin):
    key = 'scriptlets'
    schema = {
        str: str
    }

    def perform(self):
        scriptlets = self.config
        for scriptlet_name in scriptlets.keys():
            with tempfile.NamedTemporaryFile('w', prefix='{}_'.format(scriptlet_name),
                                             suffix='.sh', encoding='utf-8', delete=False) as file:
                file.write(scriptlets[scriptlet_name])
            self.run_command('/bin/bash', file.name)


class ScriptsPlugin(plugins.AbstractPlugin):
    key = 'scripts'
    schema = [str]

    def perform(self):
        scripts = self.config
        for filename in scripts:
            filename = self._expand_path(filename)
            if not os.path.isfile(filename):
                raise FileNotFoundError('The file {} doesn\'t exist'.format(filename), self.key)
            self.run_command('/bin/bash', filename)


class SnapPackagesPlugin(plugins.AbstractPlugin):
    key = 'snap-packages'
    schema = [
        str,
        {
            str: {
                schema.Optional('channel'): str,
                schema.Optional('classic'): bool,
                schema.Optional('devmode'): bool,
                schema.Optional('jailmode'): bool,
            }
        },
    ]

    def perform(self):
        packages = self.config
        for package in packages:
            if type(package) == dict:
                for package_name in package.keys():
                    options = package[package_name]
                    cmd = ['snap', 'install']
                    if 'channel' in options:
                        cmd += ['--channel', options['channel']]
                    if 'classic' in options and options['classic']:
                        cmd += ['--classic']
                    if 'devmode' in options and options['devmode']:
                        cmd += ['--devmode']
                    if 'jailmode' in options and options['jailmode']:
                        cmd += ['--jailmode']
                    cmd += [package_name]
                    self.run_command_sudo(*cmd)
            else:
                self.run_command_sudo('snap', 'install', package)


BUILTIN_PLUGINS = (
    AptPackagesPlugin,
    CreateFoldersPlugin,
    ScriptletsPlugin,
    ScriptsPlugin,
    SnapPackagesPlugin
)
