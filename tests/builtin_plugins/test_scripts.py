# -*- coding: utf-8 -*-

import os
import tempfile

from src import config


_MOCK_CONFIG = '''
$scripts:
  - hello.sh
  - scripts/foo.sh
  - scripts/bar.sh
'''

_REAL_CONFIG = '''
$scripts:
  - test01.sh
  - test02.sh
'''


def test_mock():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_MOCK_CONFIG)


def test_real():
    with tempfile.TemporaryDirectory() as tempdir:
        with open(os.path.join(tempdir, 'test01.sh'), 'w') as file:
            file.write('#!/bin/bash\ntouch result01.txt')
        with open(os.path.join(tempdir, 'test02.sh'), 'w') as file:
            file.write('#!/bin/bash\ntouch result02.txt')

        setup = config.Setup(tempdir)
        setup.load_plugins()
        setup.load_config_str(_REAL_CONFIG)
        setup.perform()
        assert set(os.listdir(tempdir)) == {'test01.sh', 'test02.sh',
                                            'result01.txt', 'result02.txt'}
