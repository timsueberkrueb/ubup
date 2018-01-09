# -*- coding: utf-8 -*-

from src import config

import os
import tempfile


_MOCK_CONFIG = '''
$folders:
  - /opt/amazing
  - foo/bar
  - ~/Holy
  - ~/Holy/Moly
'''


_REAL_CONFIG = '''
$folders:
  - test/a/b/c/d
  - test/foo
  - bar
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
        assert os.path.isdir(os.path.join(tempdir, 'test/a/b/c/d'))
        assert os.path.isdir(os.path.join(tempdir, 'test/foo'))
        assert os.path.isdir(os.path.join(tempdir, 'bar'))
