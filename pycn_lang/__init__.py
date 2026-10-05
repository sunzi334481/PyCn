# -*- coding: utf-8 -*-
"""PyCn —— 全中文语法的 Python 编程语言。"""
from .translator import translate
from .importer import install as install_import_hook

__version__ = "0.1.0"
__all__ = ["translate", "install_import_hook", "__version__"]
