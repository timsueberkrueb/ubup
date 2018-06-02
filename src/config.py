# -*- coding: utf-8 -*-

from typing import Dict, List, Type, Callable

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
from . import termcol
from . import log
from . import tree
from . import state

_OPTIONAL_META_SCHEMA = {
    schema.Optional('author'): str,
    schema.Optional('description'): str,
}


def _run_safe(f: Callable, result):
    try:
        f()
    except Exception as e:
        result += [e]


def _track_progress(indent_level: int, label: str, f: Callable):
    indent = indent_level * '  '
    widgets = [indent,
               termcol.COLORS.WARNING,
               progressbar.AnimatedMarker(), ' ', label, ' ',
               termcol.COLORS.ENDC]
    p = progressbar.ProgressBar(widgets=widgets,
                                maxval=progressbar.UnknownLength,
                                redirect_stdout=True)
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
        p.widgets = [indent, termcol.error('❌ ' + label)]
    else:
        p.widgets = [indent, termcol.success('✔ ' + label)]
    p.update(force=True)
    p.finish()
    if len(result) > 0 and isinstance(result[0], Exception):
        raise result[0]


class SetupError(Exception):
    pass


class Setup:
    def __init__(self, data_path: str = None, rerun: bool = False):
        self._data_path = data_path
        self._root = None

        self._action_schema = {}
        self._schema_root = {}
        self._rerun = rerun
        self._state = None
        self._skipped_count = 0

    @property
    def skipped_steps_count(self) -> int:
        return self._skipped_count

    def load_plugins(self):
        if self._data_path is not None:
            custom_plugins = self._load_custom_plugins()
        else:
            custom_plugins = []
        self._set_plugins(list(builtin_plugins.BUILTIN_PLUGINS) + custom_plugins)

    def load_config_file(self, filename: str):
        with open(filename) as file:
            y = yaml.YAML()
            data = y.load(file)

        if data is None:
            raise SetupError('No setup configuration found in {}.'.format(filename))

        self.load_config(data)

        self._state = state.ConfigState()
        if self._state.exists:
            self._state.load()

    def load_config_str(self, config: str):
        y = yaml.YAML()
        data = y.load(config)

        if data is None:
            raise SetupError('Trying to load empty configuration.')

        self.load_config(data)

    def load_config(self, data: Dict):
        # Support minimal schema without metadata
        if 'setup' not in data:
            data = {'setup': data}

        self._validate_schema(data)

        self._root = self._visit_node('', data['setup'])

    def perform(self, indent: bool = False, verbose: bool = False):
        self._perform_node(self._root, indent=indent, verbose=verbose)

    def _perform_node(self, node: tree.Category, indent_level: int = -1, indent: bool = False, verbose: bool = False):
        if node.name != '':
            log.information(('  ' * indent_level if indent else '') + '{}:'.format(node.name), bold=True)
        for child in node.children:
            if isinstance(child, tree.Category):
                self._perform_node(
                    node=child,
                    indent_level=indent_level + 1,
                    indent=indent,
                    verbose=verbose
                )
            elif isinstance(child, tree.Action):
                self._perform_action(
                    action=child,
                    indent_level=indent_level + 1,
                    indent=indent,
                    verbose=verbose
                )

    def _perform_action(self, action: tree.Action, indent_level: int = -1, indent: bool = False, verbose: bool = False):
        if action.name not in self._plugins:
            raise SetupError('Unknown plugin key "{}"'.format(action.name))

        if self._state is not None \
                and not self._rerun \
                and self._state.is_done(action):
            log.regular(('  ' * indent_level if indent else '') + '✓ {}'.format(action.name))
            self._skipped_count += 1
            return

        plugin_cls = self._plugins[action.name]
        plugins_inst = plugin_cls(
            config=action.body,
            data_path=self._data_path,
            verbose=verbose
        )
        _track_progress((indent_level if indent else 0), action.name, plugins_inst.perform)

        if self._state is not None:
            self._state.mark_done(action)

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

    def _visit_node(self, node_name: str, node_content: Dict):
        children = []

        for child_key in node_content.keys():
            child_value = node_content[child_key]
            if child_key.startswith('$'):
                children += [
                    self._visit_action(
                        child_key[1:],
                        child_value
                    )
                ]
            else:
                children += [
                    self._visit_node(
                        child_key,
                        child_value,
                    )
                ]
        return tree.Category(node_name, children)

    def _visit_action(self, action_key: str, action_contents):
        return tree.Action(action_key, action_contents)
