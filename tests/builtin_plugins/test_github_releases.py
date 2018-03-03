# -*- coding: utf-8 -*-

import os.path

from src import config


_MOCK_CONFIG = '''
$github-releases:
  - repo: user/repo
    release: v0.1.0
    asset: MyAssetName.zip
    target: some/path
'''

_REAL_CONFIG = '''
$github-releases:
  - repo: tim-sueberkrueb/ubup
    release: v0.1.0
    asset:  ubup-[0-9.]+-xenial-x86_64
    target: /tmp/ubup-download-v0.1.0
  - repo: tim-sueberkrueb/ubup
    release: latest
    asset:  ubup-[0-9.]+-[\w]+-x86_64
    target: /tmp/ubup-download-latest
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
    assert os.path.isfile('/tmp/ubup-download-v0.1.0')
    assert os.path.isfile('/tmp/ubup-download-latest')
