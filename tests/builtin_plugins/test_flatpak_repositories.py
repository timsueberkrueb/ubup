# -*- coding: utf-8 -*-

import subprocess

from src import config


_MOCK_CONFIG = '''
$flatpak-repositories:
  - name: foobar
    location: https://example.com/repo/example.flatpakrepo
    target: system
'''


_REAL_CONFIG = '''
$flatpak-repositories:
  - name: flathub
    location: https://flathub.org/repo/flathub.flatpakrepo
    target: user
'''


def test_mock():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_MOCK_CONFIG)


def test_real():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_REAL_CONFIG)
    setup.perform()
    output = subprocess.check_output(['bash', '-c', 'flatpak remotes | grep flathub']).decode('utf-8')
    assert output.find('flathub') != -1
