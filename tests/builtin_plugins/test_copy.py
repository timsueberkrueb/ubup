# -*- coding: utf-8 -*-

import os
import tempfile

from src import config


_MOCK_CONFIG = '''
$copy:
  source: target
  foo/*.txt: ~/Documents
  holy: moly
'''


_REAL_CONFIG = '''
$copy:
  '*.txt': target1
  moly: target2
'''


def test_mock():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_MOCK_CONFIG)


def test_real():
    test_files = (
        'abc.txt',
        'foo.txt',
        'bar.txt',
        'holy.xyz',
        'moly'
    )
    with tempfile.TemporaryDirectory() as tempdir:
        for filename in test_files:
            os.mknod(os.path.join(tempdir, filename))
        target1_dir = os.path.join(tempdir, 'target1')
        os.mkdir(target1_dir)
        target2_dir = os.path.join(tempdir, 'target2')
        os.mkdir(target2_dir)
        setup = config.Setup(tempdir)
        setup.load_plugins()
        setup.load_config_str(_REAL_CONFIG)
        setup.perform()
        assert set(os.listdir(target1_dir)) == {'abc.txt', 'foo.txt', 'bar.txt'}
        assert set(os.listdir(target2_dir)) == {'moly', }
