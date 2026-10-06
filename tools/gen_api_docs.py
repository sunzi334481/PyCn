# -*- coding: utf-8 -*-
"""
从 pycn_lang/mappings.py 自动生成《docs/基础库与预装库.md》。

用法：
    python tools/gen_api_docs.py

以 mappings.py 为唯一事实来源，保证文档与实现完全一致。
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "pycn_lang" / "mappings.py"
OUT = ROOT / "docs" / "基础库与预装库.md"


def extract_block(src: str, var: str) -> str:
    """从源码中提取 `变量名 = { ... }` 的字面量块文本。"""
    start = src.index(var + " = {")
    j = src.index("{", start)
    depth = 0
    k = j
    while k < len(src):
        c = src[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    return src[j:k + 1]


def parse_groups(block: str) -> list[tuple[str, dict[str, str]]]:
    """把字典字面量块解析为 [(分组名, {中文: 英文}), ...]。

    分组名来自块内注释行（# ---- 模块名 ---- 或 # list 列表 等）。
    没有注释头时归入「未分组」。
    """
    groups: list[tuple[str, dict[str, str]]] = []
    cur_name = "未分组"
    cur: dict[str, str] = {}

    for line in block.splitlines():
        line = line.strip()
        m = re.match(r'^#\s*-+\s*(.+?)\s*-+\s*$', line)   # # ---- math ----
        if not m:
            m = re.match(r'^#\s*(.+)$', line)              # # list 列表
        if m:
            if cur:
                groups.append((cur_name, cur))
                cur = {}
            cur_name = m.group(1).strip()
            continue
        m = re.match(r'^"(.+)"\s*:\s*"(.+)",?\s*(?:#.*)?$', line)
        if m:
            cur[m.group(1)] = m.group(2)
    if cur:
        groups.append((cur_name, cur))
    return groups


def md_table(rows: list[tuple[str, str]]) -> str:
    lines = ["| 中文 | Python |", "| --- | --- |"]
    for cn, en in rows:
        lines.append(f"| `{cn}` | `{en}` |")
    return "\n".join(lines)


def main() -> None:
    src = SRC.read_text(encoding="utf-8")

    keywords = parse_groups(extract_block(src, "KEYWORD_MAP"))
    builtin_functions = parse_groups(extract_block(src, "BUILTIN_FUNCTIONS"))
    constants = parse_groups(extract_block(src, "BUILTIN_CONSTANTS"))
    exceptions = parse_groups(extract_block(src, "EXCEPTION_MAP"))
    dunders = parse_groups(extract_block(src, "DUNDER_MAP"))
    modules = parse_groups(extract_block(src, "MODULE_MAP"))
    type_methods = parse_groups(extract_block(src, "TYPE_METHODS"))
    library_api = parse_groups(extract_block(src, "LIBRARY_API"))

    out = []
    out.append("# 基础库与预装库手册")
    out.append("")
    out.append("本手册列出 PyCn（中文 Python）的全部语言内置（基础库）与预装标准库 API。")
    out.append("内容由 `tools/gen_api_docs.py` 依据 `pycn_lang/mappings.py` 自动生成，")
    out.append("与实现保持完全一致。")
    out.append("")
    out.append("> 说明：本文「中文 → Python」映射是 **逐词替换** 的静态映射：")
    out.append("> 转译时先判关键字，再判属性位置（点号后），再判全局名字；")
    out.append("> 用户自定义的中文标识符一律原样保留，绝不会被映射误伤。")
    out.append("")

    # 1. 关键字
    kw_total = sum(len(items) for _, items in keywords)
    out.append(f"## 1. 关键字（全部 {kw_total} 个）")
    out.append("")
    out.append("关键字是语言的骨架，优先级最高——即使在属性位置也会先按关键字处理。")
    out.append("")
    kw_name, kw_map = keywords[0]
    for name, items in keywords:
        rows = sorted(items.items(), key=lambda kv: kv[0])
        out.append(md_table(rows))
        out.append("")
    out.append("**说明**：")
    out.append("")
    out.append("- `在`→`in`、`不在`→`not in`、`不是`→`is not`、`是`→`is`，覆盖成员判断与身份判断；")
    out.append("- `从` 与 `导入` 组合使用（`从 模块 导入 名字`），单独 `从` 表示 `from`；`生成` 与 `来自` 组合表示 `yield from`；")
    out.append("- `匹配/情形` 对应 `match/case` 模式匹配；`异步/等待` 对应 `async/await`；")
    out.append("- `跳过` 对应 `pass`，用于占位。")
    out.append("")

    # 2. 内置函数
    out.append("## 2. 内置函数")
    out.append("")
    fn_name, fn_map = builtin_functions[0]
    rows = sorted(fn_map.items(), key=lambda kv: kv[0])
    out.append(md_table(rows))
    out.append("")
    out.append("内置函数与 Python 内置函数行为完全一致，可在任意位置直接调用（如 `打印(...)`、`长度(...)`、`范围(...)`）。")
    out.append("")

    # 3. 内置常量
    out.append("## 3. 内置常量")
    out.append("")
    cn_name, cn_map = constants[0]
    rows = sorted(cn_map.items(), key=lambda kv: kv[0])
    out.append(md_table(rows))
    out.append("")
    out.append("`自己`→`self`、`本类`→`cls` 使类方法签名与 Python 一致且全中文；")
    out.append("`省略号`→`Ellipsis`（即 `...`），`未实现`→`NotImplemented`。")
    out.append("")

    # 4. 异常与警告
    out.append("## 4. 异常与警告")
    out.append("")
    for name, items in exceptions:
        rows = sorted(items.items(), key=lambda kv: kv[0])
        out.append(f"### {name}")
        out.append("")
        out.append(md_table(rows))
        out.append("")

    # 5. 魔术方法
    out.append("## 5. 魔术方法（dunder）与魔术变量")
    out.append("")
    out.append("在类中定义中文魔术方法即可覆写 Python 运算符/协议行为；魔术变量可读取程序环境信息。")
    out.append("")
    for name, items in dunders:
        rows = sorted(items.items(), key=lambda kv: kv[0])
        out.append(f"### {name}")
        out.append("")
        out.append(md_table(rows))
        out.append("")

    # 6. 标准库模块
    out.append("## 6. 预装标准库模块（import 模块名）")
    out.append("")
    out.append("`导入 模块名` 即可按中文名导入标准库，转译器自动补上中文别名：")
    out.append("")
    out.append("```pycn")
    out.append("导入 数学            # → import math as 数学")
    out.append("从 日期时间 导入 日期时间类  # → from datetime import datetime as 日期时间类")
    out.append("```")
    out.append("")
    mn_name, mn_map = modules[0]
    rows = sorted(mn_map.items(), key=lambda kv: kv[0])
    out.append(md_table(rows))
    out.append("")

    # 7. 类型方法
    out.append("## 7. 内置类型方法（点号后调用）")
    out.append("")
    out.append("以下方法映射仅作用于 `对象.方法名` 的属性位置，不会影响用户变量名。")
    out.append("")
    for name, items in type_methods:
        rows = sorted(items.items(), key=lambda kv: kv[0])
        out.append(f"### {name}")
        out.append("")
        out.append(md_table(rows))
        out.append("")

    # 8. 标准库 API
    out.append("## 8. 标准库 API（按模块）")
    out.append("")
    out.append("既可用于 `模块.中文API` 属性调用，也可在 `从 模块 导入 中文API` 后直接调用。")
    out.append("")
    for name, items in library_api:
        rows = sorted(items.items(), key=lambda kv: kv[0])
        out.append(f"### {name}")
        out.append("")
        out.append(md_table(rows))
        out.append("")

    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"已生成 {OUT}，共 {len(out)} 行")


if __name__ == "__main__":
    main()
