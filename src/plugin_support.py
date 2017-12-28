# -*- coding: utf-8 -*-

from typing import List, Type

import os
import sys
import importlib.util

# Add public plugins module to import path
_path = os.path.join(os.path.dirname(__file__), 'public')
if _path not in sys.path:
    sys.path.append(_path)


def load_custom_plugins(filename: str) -> List[Type]:
    spec = importlib.util.spec_from_file_location(
        filename[filename.rfind('/')+1:filename.rfind('.')], filename
    )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return [cls for name, cls in module.__dict__.items()
            if isinstance(cls, type) and name.endswith('Plugin') and name != 'AbstractPlugin']
