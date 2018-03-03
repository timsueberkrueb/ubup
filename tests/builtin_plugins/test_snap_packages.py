# -*- coding: utf-8 -*-

import os
import subprocess

from src import config


TESTS_PATH = os.path.abspath(os.path.join(os.path.basename(__file__), '..'))
ASSETS_PATH = os.path.join(TESTS_PATH, 'assets')


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
  - package: hello-world-cli_0.1_amd64.snap
    dangerous: true
'''


def test_mock():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_MOCK_CONFIG)


def test_real():
    setup = config.Setup(data_path=ASSETS_PATH)
    setup.load_plugins()
    setup.load_config_str(_REAL_CONFIG)
    setup.perform()
    check_command = ['bash', '-c', 'snap list | grep hello-world']
    output = subprocess.check_output(check_command).decode('utf-8')
    assert output.find('hello-world') != -1
    check_command = ['bash', '-c', 'snap list | grep snapcraft']
    output = subprocess.check_output(check_command).decode('utf-8')
    assert output.find('snapcraft') != -1
    check_command = ['bash', '-c', 'snap list | grep hello-world-cli']
    output = subprocess.check_output(check_command).decode('utf-8')
    assert output.find('hello-world-cli') != -1
