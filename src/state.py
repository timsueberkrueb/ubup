# -*- coding: utf-8 -*-

import os
import io
import ruamel.yaml as yaml

from . import tree


class ConfigState:
    def __init__(self, data_path: str, filename: str, remote: str = 'local'):
        self._performed_actions = []
        self._data_path = data_path
        self._state_dir = os.path.join(data_path, '.ubup')
        if not os.path.isdir(self._state_dir):
            os.makedirs(self._state_dir, exist_ok=True)
        self._state_filepath = os.path.join(
            self._state_dir,
            'state_{}_{}.yaml'.format(remote, self._encode_filename(filename))
        )

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
