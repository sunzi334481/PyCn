# -*- coding: utf-8 -*-
"""PyCn 导入钩子单元测试。"""
import importlib
import sys
import tempfile
import unittest
from pathlib import Path

from pycn_lang.importer import install


class TestImportHook(unittest.TestCase):
    def setUp(self):
        install()
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)
        sys.path.insert(0, str(self.tmpdir))

    def tearDown(self):
        # 清理本次导入的模块与路径
        for name in list(sys.modules):
            if name in ("工具", "我的包", "我的包.子模块", "我的包.工具"):
                del sys.modules[name]
        if str(self.tmpdir) in sys.path:
            sys.path.remove(str(self.tmpdir))
        self.tmp.cleanup()

    def test_import_pycn_module(self):
        (self.tmpdir / "工具.pycn").write_text(
            "定义 加倍(x):\n    返回 x * 2\n", encoding="utf-8"
        )
        module = importlib.import_module("工具")
        self.assertEqual(module.加倍(21), 42)

    def test_import_pycn_package(self):
        pkg = self.tmpdir / "我的包"
        pkg.mkdir()
        (pkg / "__init__.pycn").write_text(
            "从 .子模块 导入 问候\n", encoding="utf-8"
        )
        (pkg / "子模块.pycn").write_text(
            "定义 问候():\n    返回 '你好'\n", encoding="utf-8"
        )
        module = importlib.import_module("我的包")
        self.assertEqual(module.问候(), "你好")

    def test_submodule_direct(self):
        pkg = self.tmpdir / "我的包"
        pkg.mkdir()
        (pkg / "__init__.pycn").write_text("", encoding="utf-8")
        (pkg / "工具.pycn").write_text(
            "值 = 42\n", encoding="utf-8"
        )
        module = importlib.import_module("我的包.工具")
        self.assertEqual(module.值, 42)

    def test_standard_library_still_works(self):
        # 标准库不受影响
        math = importlib.import_module("math")
        self.assertTrue(hasattr(math, "sqrt"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
