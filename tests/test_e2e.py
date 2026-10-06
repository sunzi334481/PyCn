# -*- coding: utf-8 -*-
"""端到端测试：通过 CLI 实际运行示例 .pycn 程序。"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def run_pycn(script: Path, *args: str):
    return subprocess.run(
        [sys.executable, "-m", "pycn_lang", "run", str(script), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(ROOT),
    )


class TestExamplesRun(unittest.TestCase):
    def test_smoke_example(self):
        proc = run_pycn(EXAMPLES / "冒烟测试.pycn")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("冒烟测试全部通过", proc.stdout)

    def test_fibonacci_example(self):
        proc = run_pycn(EXAMPLES / "斐波那契.pycn")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("斐波那契数列", proc.stdout)

    def test_scores_example(self):
        proc = run_pycn(EXAMPLES / "学生成绩.pycn")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("成绩统计", proc.stdout)

    def test_oop_example(self):
        proc = run_pycn(EXAMPLES / "面向对象.pycn")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("面向对象演示", proc.stdout)

    def test_stdlib_example(self):
        proc = run_pycn(EXAMPLES / "标准库演示.pycn")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("标准库演示完成", proc.stdout)

    def test_multifile_main(self):
        proc = run_pycn(EXAMPLES / "模块演示_主.pycn")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("多文件模块演示完成", proc.stdout)

    def test_exception_example(self):
        proc = run_pycn(EXAMPLES / "异常处理演示.pycn")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("异常处理演示完成", proc.stdout)

    def test_cli_arguments(self):
        proc = run_pycn(EXAMPLES / "命令行参数.pycn", "张三", "李四")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("张三", proc.stdout)
        self.assertIn("李四", proc.stdout)

    def test_compile_then_run(self):
        proc = subprocess.run(
            [sys.executable, "-m", "pycn_lang", "compile",
             str(EXAMPLES / "斐波那契.pycn"), "-o", "-"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("def ", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
