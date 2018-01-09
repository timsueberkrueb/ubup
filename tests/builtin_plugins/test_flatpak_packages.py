# -*- coding: utf-8 -*-

import subprocess

from src import config


_MOCK_CONFIG = '''
$flatpak-packages:
  - foo.flatpak
  - bar.flatpakref
  - https://example.com/foo.flatpakref
  - package: https://example.com/bar.flatpakref
    type: ref
    target: user
  - package: org.freedesktop.Platform
    remote: flathub
    type: runtime
'''


_REAL_CONFIG = '''
$flatpak-repositories:
  - name: flathub
    location: https://flathub.org/repo/flathub.flatpakrepo
    target: user
$flatpak-packages:
  - package: org.freedesktop.Platform
    remote: flathub
    type: runtime
    target: user
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
    output = subprocess.check_output(['bash', '-c', 'flatpak list | grep org.freedesktop.Platform']).decode('utf-8')
    assert output.find('org.freedesktop.Platform') != -1
