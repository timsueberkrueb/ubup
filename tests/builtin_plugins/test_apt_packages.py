# -*- coding: utf-8 -*-

import subprocess

from src import config


_MOCK_CONFIG = '''
$apt-packages:
  - foo
  - bar
  - cool
  - stuff
'''

_REAL_CONFIG = '''
$apt-packages: [cowsay]
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
    check_command = ['bash', '-c', 'dpkg --get-selections | grep -v deinstall | grep cowsay']
    output = subprocess.check_output(check_command).decode('utf-8')
    assert output.find('cowsay') != -1
