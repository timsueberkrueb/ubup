# -*- coding: utf-8 -*-

from src import config


_MINIMALISTIC_CONFIG = '''
$apt-packages: [holy, moly]
'''


_SIMPLE_CONFIG = '''
category:
  test-category:
    $apt-packages:
      - foo
      - bar
$apt-packages: [amazing, packages]
'''

_ADVANCED_CONFIG = '''
author: John Doe <john.doe@example.com>
description: |
  Lorem ipsum dolor sit amet.
setup:
  test-category:
    $apt-packages: [foo, bar]
  abc:
    $apt-packages: [cool, stuff]
'''


def test_load_minimalistic_config():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_MINIMALISTIC_CONFIG)


def test_load_simple_config():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_SIMPLE_CONFIG)


def test_load_advanced_config():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_ADVANCED_CONFIG)
