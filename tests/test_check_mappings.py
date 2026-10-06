# -*- coding: utf-8 -*-
"""扫描 mappings.py 源文本，报告每个映射表内部的重复键（Python dict 会静默覆盖）。

以 unittest 用例形式存在，可被 `python -m unittest discover tests` 自动收集。
"""
import re
import unittest
from pathlib import Path
from collections import defaultdict

MAPPINGS_SRC = Path(__file__).resolve().parents[1] / "pycn_lang" / "mappings.py"


def find_duplicate_keys() -> list:
    """返回 [(表名, 键, [行号...]), ...]，仅含重复键。"""
    text = MAPPINGS_SRC.read_text(encoding="utf-8")
    current = None
    seen = defaultdict(list)
    for lineno, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^([A-Z_]+)\s*=\s*\{", line)
        if m:
            current = m.group(1)
        if line.strip() == "}":
            current = None
        km = re.match(r'^\s*"([^"]+)"\s*:', line)
        if km and current:
            seen[(current, km.group(1))].append(lineno)
    return [(table, key, lines) for (table, key), lines in seen.items() if len(lines) > 1]


class TestMappingsConsistency(unittest.TestCase):
    def test_no_duplicate_keys(self):
        problems = find_duplicate_keys()
        self.assertEqual(
            problems, [],
            f"发现表内重复键：{problems}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
