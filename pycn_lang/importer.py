# -*- coding: utf-8 -*-
"""
PyCn 导入钩子（import hook）。

安装后，Python 导入系统可以直接加载 .pycn 文件：
  - 支持单文件模块： 工具.pycn      -> import 工具
  - 支持包：         我的包/__init__.pycn
  - 支持子模块、相对导入；
  - 标准库中文模块名在转译期已替换为英文，走 Python 默认查找；
  - 本 finder 注册在 meta_path 末尾，标准库优先，避免意外遮蔽。
"""
import sys
from pathlib import Path
from importlib.machinery import ModuleSpec

from .translator import translate

PYCN_EXT = ".pycn"
INIT_FILE = "__init__" + PYCN_EXT


class PycnLoader:
    """把 .pycn 转译后作为普通模块执行。"""

    def __init__(self, path: Path):
        self.path = str(path)

    def create_module(self, spec):
        return None  # 使用默认模块对象

    def exec_module(self, module):
        source = Path(self.path).read_text(encoding="utf-8-sig")
        translated = translate(source)
        code = compile(translated, self.path, "exec")
        # 注册原文到 linecache：traceback / inspect 显示中文源码而非转译后的英文
        import linecache
        linecache.cache[self.path] = (
            len(source), None, [ln + "\n" for ln in source.splitlines()], self.path,
        )
        module.__file__ = self.path
        exec(code, module.__dict__)


class PycnFinder:
    """按 sys.path / 包路径查找 .pycn 模块与包。"""

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        parts = fullname.split(".")
        leaf = parts[-1]
        bases = list(path) if path else list(sys.path)
        bases.insert(0, "")  # "" 表示当前工作目录

        seen = set()
        for base in bases:
            if not isinstance(base, str) or base in seen:
                continue
            seen.add(base)
            bpath = Path(base) if base else Path.cwd()

            # 单文件模块
            module_file = bpath / (leaf + PYCN_EXT)
            if module_file.is_file():
                return ModuleSpec(
                    fullname,
                    PycnLoader(module_file),
                    origin=str(module_file),
                )

            # 包（含 __init__.pycn）
            package_dir = bpath / leaf
            init_file = package_dir / INIT_FILE
            if init_file.is_file():
                spec = ModuleSpec(
                    fullname,
                    PycnLoader(init_file),
                    origin=str(init_file),
                    is_package=True,
                )
                spec.submodule_search_locations = [str(package_dir)]
                return spec
        return None


_installed = False


def install():
    """注册导入钩子（幂等）。置于默认 PathFinder 之前。"""
    global _installed
    if not _installed:
        from importlib.machinery import PathFinder
        if PycnFinder in sys.meta_path:
            sys.meta_path.remove(PycnFinder)
        idx = sys.meta_path.index(PathFinder)
        sys.meta_path.insert(idx, PycnFinder)
        # 清除缓存，防止此前已把纯目录缓存为命名空间包
        sys.path_importer_cache.clear()
        _installed = True
