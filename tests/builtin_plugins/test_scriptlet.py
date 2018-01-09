# -*- coding: utf-8 -*-

import os
import tempfile

from src import config


_MOCK_CONFIG = '''
$scriptlet: |
    echo "Hello World"
    # ...
'''

_REAL_CONFIG = '''
$scriptlet: |
    touch test.txt
'''


def test_mock():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_MOCK_CONFIG)


def test_real():
    with tempfile.TemporaryDirectory() as tempdir:
        setup = config.Setup(tempdir)
        setup.load_plugins()
        setup.load_config_str(_REAL_CONFIG)
        setup.perform()
        assert os.listdir(tempdir) == ['test.txt']
