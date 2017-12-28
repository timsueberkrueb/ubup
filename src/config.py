# -*- coding: utf-8 -*-

from typing import List, Type, Dict

import os
import glob
import yaml
import schema
import math

from . import builtin_plugins
from . import plugin_support
from . import plugins
from . import log


# Names that cannot be used as plugin keys
_RESERVED_PLUGIN_NAMES = (
    'steps',
    'author',
    'description',
    'revision',
    'version',
    'last_updated'
)


_OPTIONAL_META_SCHEMA = {
    schema.Optional('author'): str,
    schema.Optional('description'): str,
    schema.Optional('revision'): int,
    schema.Optional('version'): str,
    schema.Optional('last_updated'): str,
}


class SetupError(Exception):
    pass


class Setup:
    def __init__(self, data_path: str):
        self._data_path = data_path
        self._plugins_schema_root = {}
        self._advanced_schema_root = {}
        self._plugins: Dict[str, Type[plugins.AbstractPlugin]] = []
        self._config = None

    def load_plugins(self):
        custom_plugins = self._load_custom_plugins()
        self._set_plugins(list(builtin_plugins.BUILTIN_PLUGINS) + custom_plugins)

    def load_config(self, filename: str):
        with open(filename) as file:
            data = yaml.load(file)

        self._validate_schema(data)

        if 'steps' not in data:
            data = {'steps': [data]}

        self._config = data

    def perform(self):
        steps_count = len(self._config['steps'])
        step_number_max_len = math.ceil(math.log10(steps_count + 1))
        step_number_placeholder = '{' + ':0{}d'.format(step_number_max_len) + '}'
        for i, step in enumerate(self._config['steps']):
            if steps_count != 1:
                log.header(f'Performing step {step_number_placeholder.format(i+1)} '
                           f'of {step_number_placeholder.format(steps_count)}')
            for plugin_key in step.keys():
                if plugin_key not in self._plugins:
                    raise SetupError(f'Unknown plugin "{plugin_key}" in configuration')
                plugin_config = step[plugin_key]
                plugin_cls = self._plugins[plugin_key]
                plugin_inst = plugin_cls(plugin_config, self._data_path)
                log.information(f'Performing plugin {plugin_key}')
                plugin_inst.perform()

    def _load_custom_plugins(self) -> List[Type[plugins.AbstractPlugin]]:
        plugins_list = []
        plugins_folder = os.path.join(self._data_path, 'plugins')
        if os.path.isdir(plugins_folder):
            for filename in glob.glob(os.path.join(plugins_folder, '*.py')):
                plugins_list += plugin_support.load_custom_plugins(filename)
        return plugins_list

    def _set_plugins(self, plugins_list: List[Type[plugins.AbstractPlugin]]):
        self._plugins_schema_root = {}
        self._plugins = {}
        for plugin in plugins_list:
            if plugin.key == _RESERVED_PLUGIN_NAMES:
                raise SetupError(f'Plugin with reserved name {plugin.key}')
            if plugin.key in self._plugins:
                raise SetupError(f'Duplicate plugin key {plugin.key}')
            self._plugins[plugin.key] = plugin
            self._plugins_schema_root[schema.Optional(plugin.key)] = plugin.schema
        self._advanced_schema_root = {
            **_OPTIONAL_META_SCHEMA,
            'steps': [
                self._plugins_schema_root
            ]
        }

    def _validate_schema(self, data):
        # Require the root structure to be a dictionary
        schema.Schema(dict).validate(data)

        # Allow a list of steps for control over execution sequence
        if 'steps' in data:
            steps_schema = schema.Schema(self._advanced_schema_root)
            steps_schema.validate(data)
        # Simple schema variation consists of just one step
        else:
            simple_schema = schema.Schema(self._plugins_schema_root)
            simple_schema.validate(data)
