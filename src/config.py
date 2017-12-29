# -*- coding: utf-8 -*-

from typing import List, Type, Dict, Callable

import os
import glob
import ruamel.yaml as yaml
import schema
import progressbar
import threading
import itertools
import time

from . import builtin_plugins
from . import plugin_support
from . import plugins
from . import log
from . import termcol


# Names that cannot be used as plugin keys
_RESERVED_PLUGIN_NAMES = (
    'author',
    'description',
    'setup'
)


_OPTIONAL_META_SCHEMA = {
    schema.Optional('author'): str,
    schema.Optional('description'): str,
}


def _run_safe(f: Callable, result):
    try:
        f()
    except Exception as e:
        result += [e]


def _track_progress(label: str, f: Callable):
    widgets = [termcol.COLORS.INFORMATION, label, ' ',
               progressbar.AnimatedMarker(), termcol.COLORS.ENDC]
    p = progressbar.ProgressBar(widgets=widgets,
                                maxval=progressbar.UnknownLength)
    p.start()
    result = []
    thread = threading.Thread(target=_run_safe, args=(f, result))
    thread.start()
    for progress_count in itertools.count():
        if not thread.is_alive():
            break
        p.update(progress_count)
        time.sleep(0.1)
    if len(result) > 0:
        p.widgets = [termcol.error(label + ' ❌')]
    else:
        p.widgets = [termcol.success(label + ' ✓')]
    p.update(force=True)
    p.finish()
    for r in result:
        if isinstance(r, Exception):
            raise r


class SetupError(Exception):
    pass


class Setup:
    def __init__(self, data_path: str):
        self._data_path = data_path
        self._plugins = {}
        self._config = None

        self._action_schema = {}
        self._schema_root = {}

    def load_plugins(self):
        custom_plugins = self._load_custom_plugins()
        self._set_plugins(list(builtin_plugins.BUILTIN_PLUGINS) + custom_plugins)

    def load_config(self, filename: str):
        with open(filename) as file:
            y = yaml.YAML()
            data = y.load(file)

        # Support minimal schema without metadata
        if 'setup' not in data:
            data = {'setup': data}

        self._validate_schema(data)

        self._config = data

    def perform(self, indent: bool=False):
        root = self._config['setup']
        self._perform_node(root, indent=indent)

    def _perform_node(self, node_content: Dict, node_name: str='', indent_level: int=-1, indent: bool=False):
        if node_name != '':
            log.header(('  ' * indent_level if indent else '') + '🔖{}:'.format(node_name))
        for child_key in node_content.keys():
            child_value = node_content[child_key]
            if child_key.startswith('$'):
                self._perform_action(
                    child_key[1:],
                    child_value,
                    indent_level=indent_level+1, indent=indent
                )
            else:
                self._perform_node(
                    child_value,
                    node_name=child_key,
                    indent_level=indent_level+1,
                    indent=indent
                )

    def _perform_action(self, key: str, config: object, indent_level: int=-1, indent: bool=False):
        if key not in self._plugins:
            raise SetupError('Unknown plugin key "{}"'.format(key))
        plugin_cls = self._plugins[key]
        plugins_inst = plugin_cls(config, self._data_path)
        _track_progress(('  ' * indent_level if indent else '') + '⚡{}'.format(key), plugins_inst.perform)

    def _load_custom_plugins(self) -> List[Type[plugins.AbstractPlugin]]:
        plugins_list = []
        plugins_folder = os.path.join(self._data_path, 'plugins')
        if os.path.isdir(plugins_folder):
            for filename in glob.glob(os.path.join(plugins_folder, '*.py')):
                plugins_list += plugin_support.load_custom_plugins(filename)
        return plugins_list

    def _set_plugins(self, plugins_list: List[Type[plugins.AbstractPlugin]]):
        self._action_schema = {}
        self._plugins = {}
        for plugin in plugins_list:
            if plugin.key == _RESERVED_PLUGIN_NAMES:
                raise SetupError('Plugin with reserved name {}'.format(plugin.key))
            if plugin.key in self._plugins:
                raise SetupError('Duplicate plugin key {}'.format(plugin.key))
            self._plugins[plugin.key] = plugin
            self._action_schema[schema.Optional('$' + plugin.key)] = plugin.schema
        self._category_schema = {
            # Recursive validation of child categories (may not start with '$')
            schema.Optional(lambda key: type(key) == str and not key.startswith('$')):
                lambda value: schema.Schema(self._category_schema).validate(value),
            # Validation of child actions (must start with '$')
            **self._action_schema,
        }
        self._schema_root = {
            **_OPTIONAL_META_SCHEMA,
            'setup': self._category_schema
        }

    def _validate_schema(self, data):
        s = schema.Schema(self._schema_root)
        s.validate(data)
