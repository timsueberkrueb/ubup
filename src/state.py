# -*- coding: utf-8 -*-

import os
import io
import ruamel.yaml as yaml

from . import tree


STATE_CONFIG_DIR = os.path.expanduser('~/.config/ubup')
STATE_CONFIG_PATH = '{}/state.yaml'.format(STATE_CONFIG_DIR)


class ConfigState:
    def __init__(self):
        self._performed_actions = []
        if not os.path.isdir(STATE_CONFIG_DIR):
            os.makedirs(STATE_CONFIG_DIR, exist_ok=True)
        self._state_filepath = STATE_CONFIG_PATH

    @property
    def exists(self) -> bool:
        return os.path.isfile(self._state_filepath)

    def is_done(self, action_to_perform: tree.Action) -> bool:
        action_data = self._serialize_action(action_to_perform)
        return action_data in self._performed_actions

    def mark_done(self, performed_action: tree.Action, auto_save: bool = True):
        self._performed_actions += [self._serialize_action(performed_action)]
        if auto_save:
            self.save()

    def save(self):
        with open(self._state_filepath, 'w') as file:
            yaml.dump(self._performed_actions, file)

    def load(self):
        with open(self._state_filepath) as file:
            y = yaml.YAML(typ='base')
            self._performed_actions = y.load(file)

    @staticmethod
    def _encode_filename(filename) -> str:
        filename = os.path.basename(filename)
        filename = filename.replace('_', '__')
        filename = filename.replace('.', '_')
        return filename

    @staticmethod
    def _purify_yaml(yaml_obj):
        # Convert YAML type to pure Python type
        # FIXME: This is fairly hacky.
        # There must be a better way to do this.
        temp = io.StringIO()
        y_roundtrip = yaml.YAML(typ='rt')
        y_roundtrip.dump(yaml_obj, temp)
        temp.seek(0)
        y_base = yaml.YAML(typ='base')
        return y_base.load(temp)

    @staticmethod
    def _serialize_action(action: tree.Action):
        return ConfigState._purify_yaml({
            'name': action.name,
            'body': action.body
        })
