# -*- coding: utf-8 -*-

from src import config
from src.builtin_plugins import PPAsPlugin


_MOCK_CONFIG = '''
$ppas:
  - foo/bar
  - holy/moly
'''

_REAL_CONFIG = '''
$ppas:
  - alexlarsson/flatpak
'''


class PPAsHelper(PPAsPlugin):
    def is_ppa_installed(self, ppa: str):
        return ppa in self._get_existing_ppas()


def test_mock():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_MOCK_CONFIG)


def test_real():
    setup = config.Setup()
    setup.load_plugins()
    setup.load_config_str(_REAL_CONFIG)
    setup.perform()
    assert PPAsHelper().is_ppa_installed('alexlarsson/flatpak')
