# -*- coding: utf-8 -*-
"""从 mappings.py 生成三套编辑器词表，保证高亮与语言实现同步。

覆盖文件：
  - editors/vscode-pycn/syntaxes/pycn.tmLanguage.json
  - editors/jetbrains-pycn/src/main/kotlin/com/pycn/plugin/PycnLexer.kt
  - editors/visualstudio-pycn/PycnVsPackage/PycnClassifier.cs

用法：
  python tools/gen_editor_keywords.py          # 生成并写回三份文件
  python tools/gen_editor_keywords.py --check  # 仅校验词表一致性，不写文件
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pycn_lang import mappings as M

# ------------------------------------------------------------------
# 词表分组（与 VSCode tmLanguage 的规则保持一致；「是」并入 control）
# ------------------------------------------------------------------
CONTROL = ["如果", "否则若", "否则", "对于", "在", "当", "跳出",
           "继续", "返回", "生成", "来自", "匹配", "情形", "是"]
OTHER = ["尝试", "捕获", "最终", "抛出", "导入", "从", "作为", "伴随",
         "断言", "删除", "全局", "非局部", "异步", "等待", "跳过", "匿名"]
LOGICAL = ["且", "或", "非", "不在", "不是"]
CONSTANTS = ["真", "假", "空", "省略号", "未实现"]
SELF = ["自己", "本类"]


def validate_groups() -> None:
    """校验分组恰好覆盖全部关键字与内置常量。"""
    kws = set(M.KEYWORD_MAP)
    # 定义/类 由 tmLanguage 的 definitions 规则（captures）单独覆盖
    covered = set(CONTROL) | set(OTHER) | set(LOGICAL) | {"真", "假", "空", "定义", "类"}
    assert covered == kws, f"关键字分组不一致：缺 {kws - covered}，多 {covered - kws}"
    assert set(CONSTANTS) - {"真", "假", "空"} <= set(M.BUILTIN_CONSTANTS), "常量分组错误"
    assert set(SELF) == {"自己", "本类"}, "self 分组错误"


def fmt_match(words: list) -> str:
    """VSCode tmLanguage 的 match 字符串（中文词边界）。"""
    return "(?<![\\u4e00-\\u9fff])(" + "|".join(words) + ")(?![\\u4e00-\\u9fff])"


def fmt_kotlin(name: str, words: list, indent: str = "        ") -> str:
    lines = [f"val {name} = setOf("]
    row = []
    for w in words:
        row.append(f'"{w}"')
        if len(row) == 8:
            lines.append(indent + ", ".join(row) + ",")
            row = []
    if row:
        lines.append(indent + ", ".join(row))
    lines.append(indent.rstrip() + ")")
    return "\n".join(lines)


def fmt_csharp(name: str, words: list) -> str:
    lines = [f"private static readonly string[] {name} =", "        {"]
    row = []
    for w in words:
        row.append(f'"{w}"')
        if len(row) == 8:
            lines.append("            " + ", ".join(row) + ",")
            row = []
    if row:
        lines.append("            " + ", ".join(row))
    lines.append("        };")
    return "\n".join(lines)


# ------------------------------------------------------------------
# VSCode tmLanguage
# ------------------------------------------------------------------
VSC_TM = ROOT / "editors" / "vscode-pycn" / "syntaxes" / "pycn.tmLanguage.json"

TM_RULES = [
    ("keyword.control.pycn", CONTROL),
    ("keyword.other.pycn", OTHER),
    ("keyword.operator.logical.pycn", LOGICAL),
    ("constant.language.pycn", CONSTANTS),
    ("variable.language.this.pycn", SELF),
    ("support.function.builtin.pycn", list(M.BUILTIN_FUNCTIONS)),
    ("support.type.exception.pycn", list(M.EXCEPTION_MAP)),
]

# 字符串前缀正则片段（中文组合：格原/原格=fr/rf，原字/字原=rb/br；f 与 b 互斥）
FSTRING_PREFIX = "格|格原|原格|f|fr|rf"
RAW_PREFIX = "原|字|原字|字原|r|b|br|rb"


def patch_tmlanguage(text: str) -> str:
    for name, words in TM_RULES:
        pat = re.compile(
            r'("name": "' + re.escape(name) + r'",\s*"match": ")([^"]*)(")'
        )
        text, n = pat.subn(lambda m: m.group(1) + fmt_match(words) + m.group(3), text)
        assert n == 1, f"tmLanguage 规则 {name} 未找到或重复（{n} 处）"
    # 字符串前缀：interpolated（格原/原格 组合，去非法 fb/bf）
    text = text.replace("(?:格|f|fr|rf|fb|bf)", f"(?:{FSTRING_PREFIX})")
    # quoted（原字/字原 组合）
    text = text.replace("(?:原|字|r|b|br|rb)", f"(?:{RAW_PREFIX})")
    return text


# ------------------------------------------------------------------
# JetBrains Kotlin
# ------------------------------------------------------------------
KOTLIN = ROOT / "editors" / "jetbrains-pycn" / "src" / "main" / "kotlin" / "com" / "pycn" / "plugin" / "PycnLexer.kt"

KOTLIN_TABLES = [
    ("KEYWORDS", CONTROL + OTHER + LOGICAL + ["真", "假", "空"]),
    ("BUILTINS", list(M.BUILTIN_FUNCTIONS)),
    ("EXCEPTIONS", list(M.EXCEPTION_MAP)),
]


def patch_kotlin(text: str) -> str:
    for name, words in KOTLIN_TABLES:
        pat = re.compile(r"val " + name + r" = setOf\(.*?\)\n", re.DOTALL)
        text, n = pat.subn(fmt_kotlin(name, words) + "\n", text)
        assert n == 1, f"Kotlin 表 {name} 未找到或重复（{n} 处）"
    return text


# ------------------------------------------------------------------
# Visual Studio C#
# ------------------------------------------------------------------
CSHARP = ROOT / "editors" / "visualstudio-pycn" / "PycnVsPackage" / "PycnClassifier.cs"

CSHARP_TABLES = [
    ("Keywords", CONTROL + OTHER + LOGICAL + ["真", "假", "空"]),
    ("Builtins", list(M.BUILTIN_FUNCTIONS)),
    ("Exceptions", list(M.EXCEPTION_MAP)),
]


def patch_csharp(text: str) -> str:
    for name, words in CSHARP_TABLES:
        pat = re.compile(
            r"private static readonly string\[\] " + name + r" =\s*\{(.*?)\};",
            re.DOTALL,
        )
        text, n = pat.subn(fmt_csharp(name, words), text)
        assert n == 1, f"C# 表 {name} 未找到或重复（{n} 处）"
    return text


def main() -> int:
    validate_groups()
    if "--check" in sys.argv:
        print("词表分组校验通过：")
        print(f"  关键字 {len(M.KEYWORD_MAP)} 个（文档应写 40）")
        print(f"  内置函数 {len(M.BUILTIN_FUNCTIONS)} 个")
        print(f"  异常 {len(M.EXCEPTION_MAP)} 个")
        return 0

    for path, patch in ((VSC_TM, patch_tmlanguage),
                        (KOTLIN, patch_kotlin),
                        (CSHARP, patch_csharp)):
        text = path.read_text(encoding="utf-8")
        new = patch(text)
        path.write_text(new, encoding="utf-8")
        print(f"已更新 {path.relative_to(ROOT)}")
    print("完成：三套编辑器词表已与 mappings.py 同步")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
