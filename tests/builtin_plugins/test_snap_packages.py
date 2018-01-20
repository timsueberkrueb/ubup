# -*- coding: utf-8 -*-

import subprocess

from src import config


_MOCK_CONFIG = '''
$snap-packages:
  - foo
  - package: bar
    classic: true
    channel: latest/stable
    jailmode: false
    devmode: false
'''

_REAL_CONFIG = '''
$snap-packages:
  - hello-world
  - package: snapcraft
    classic: true
    channel: latest/edge
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
    check_command = ['bash', '-c', 'snap list | grep hello-world']
    output = subprocess.check_output(check_command).decode('utf-8')
    assert output.find('hello-world') != -1
    check_command = ['bash', '-c', 'snap list | grep snapcraft']
    output = subprocess.check_output(check_command).decode('utf-8')
    assert output.find('snapcraft') != -1
