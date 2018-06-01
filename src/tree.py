# -*- coding: utf-8 -*-

from typing import List, Union, Dict


class Action:
    def __init__(self, name: str, body: Dict):
        self.name = name
        self.body = body


class Category:
    def __init__(self, name: str = '', children: List[Union[Action, 'Category']] = None):
        self.name = name
        self.children = children or []
