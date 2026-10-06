# -*- coding: utf-8 -*-
"""
PyCn 转译器：把中文 Python 源码（.pycn）逐 token 转译为标准 Python 源码。

设计要点：
  - 手写扫描器，精确区分 注释 / 字符串 / 名字 / 数字 / 运算符；
  - 行列保持（不增删换行），因此转译后报错行号与源码一致；
  - 用户自定义的中文标识符原样保留（Python 3 原生支持 Unicode 标识符）；
  - 支持中文字符串前缀：格=f，原=r，字=b；
  - 支持 f-string（格字符串）内部表达式的中文转译、!表示/!字符串/!码 转换标志；
  - 特殊字符串 "__主__" -> "__main__"。
"""
import re

from . import mappings as M


# ------------------------------------------------------------
# 字符判定
# ------------------------------------------------------------
def _is_ident_start(c: str) -> bool:
    return c == "_" or c.isalpha()


def _is_ident_cont(c: str) -> bool:
    return c == "_" or c.isalnum()


_QUOTES = ("'", '"')


# ------------------------------------------------------------
# 名字翻译
# ------------------------------------------------------------
def _translate_name(name: str, after_dot: bool, user_names: set) -> str:
    """翻译单个名字。

    after_dot=True（属性位置）：只查类型方法/库 API 表，其余属性名原样保留——
    不再翻译关键字与全局内置名，避免产出 `x.True` 这类怪异属性。
    普通位置：关键字优先；全局内置名仅在未被用户用作定义名时翻译。
    """
    if after_dot:
        if name in M.ATTRIBUTE_MAP:
            return M.ATTRIBUTE_MAP[name]
        return name
    # 关键字优先
    if name in M.KEYWORD_MAP:
        return M.KEYWORD_MAP[name]
    # 全局内置名：若用户已把它当作变量/参数等定义过，则保留中文
    if name in M.GLOBAL_NAME_MAP and name not in user_names:
        return M.GLOBAL_NAME_MAP[name]
    # 用户自定义标识符，原样保留
    return name


# ------------------------------------------------------------
# 字符串前缀
# ------------------------------------------------------------
def _convert_prefix(name: str) -> str | None:
    """若 name 是字符串前缀（中文或英文），返回英文前缀；否则返回 None。"""
    if not name:
        return None
    if all(ch in M.STRING_PREFIX_CHARS for ch in name):
        result = "".join(M.STRING_PREFIX_CHARS[ch] for ch in name)
        # 去重排序无意义，Python 要求合法组合：f/r/b，rb/br 合法
        if result in ("f", "r", "b", "fr", "rf", "br", "rb", "fb", "bf"):
            return result
        return None
    # 英文前缀白名单：f/r/b 及其合法组合；u/U 前缀已从 Python 3.12+ 移除
    if all(ch in "frbFRB" for ch in name):
        return name
    return None


# ------------------------------------------------------------
# 数字扫描
# ------------------------------------------------------------
def _scan_number(s: str, i: int) -> int:
    """扫描数字字面量，返回结束下标。s[i] 为数字，或 s[i]=='.' 且后一位为数字。"""
    n = len(s)
    j = i
    # 十六 / 八 / 二 进制
    if s[j] == "0" and j + 1 < n and s[j + 1] in "xXoObB":
        j += 2
        while j < n and (s[j].isalnum() or s[j] == "_"):
            j += 1
        return j
    # 十进制整数 / 浮点
    while j < n and (s[j].isdigit() or s[j] == "_"):
        j += 1
    if j < n and s[j] == "." and (j + 1 >= n or s[j + 1] != "."):
        j += 1
        while j < n and (s[j].isdigit() or s[j] == "_"):
            j += 1
    # 指数
    if j < n and s[j] in "eE":
        k = j + 1
        if k < n and s[k] in "+-":
            k += 1
        if k < n and s[k].isdigit():
            j = k
            while j < n and (s[j].isdigit() or s[j] == "_"):
                j += 1
    # 虚数后缀
    if j < n and s[j] in "jJ":
        j += 1
    return j


# ------------------------------------------------------------
# f-string 表达式扫描
# ------------------------------------------------------------
def _scan_fstring_expression(s: str, i: int) -> tuple[str, int]:
    """
    s[i-1] == '{'，扫描 f-string 花括号内部直到匹配的 '}'。
    返回 (转译后的花括号整体（含外层 {}）, 结束下标（'}' 之后）)。
    """
    n = len(s)
    j = i
    depth = 0
    expr_end = None  # 顶层 : 或 ! 的位置
    while j < n:
        c = s[j]
        if c in _QUOTES:
            _, j = _scan_string(s, j, "")
            continue
        if c in "([{":
            depth += 1
            j += 1
            continue
        if c in ")]}":
            if depth == 0 and c == "}":
                break
            depth -= 1
            j += 1
            continue
        if depth == 0 and c in ":!":
            expr_end = j
            break
        j += 1

    # 未找到匹配的 }：原样返回剩余文本，交给 Python 报出正确位置的 SyntaxError
    if j >= n:
        return "{" + s[i:j], j

    if expr_end is None:
        expr_text = s[i:j]
        tail = ""
    else:
        expr_text = s[i:expr_end]
        # 处理转换标志 !表示/!字符串/!码，其余（含 :格式说明）原样
        k = expr_end
        tail = ""
        if s[k] == "!":
            m = k + 1
            while m < n and _is_ident_cont(s[m]):
                m += 1
            conv = s[k + 1:m]
            tail = "!" + M.FSTRING_CONVERSIONS.get(conv, conv)
            k = m
        # 格式说明符：扫描到匹配的 '}'，跟踪嵌套花括号与字符串
        spec_start = k
        spec_depth = 0
        while k < n:
            c = s[k]
            if c in _QUOTES:
                _, k = _scan_string(s, k, "")
                continue
            if c == "{":
                if k + 1 < n and s[k + 1] == "{":
                    k += 2
                    continue
                spec_depth += 1
                k += 1
                continue
            if c == "}":
                if spec_depth > 0:
                    spec_depth -= 1
                    k += 1
                    continue
                break
            k += 1
        tail += s[spec_start:k]
        j = k

    translated_expr = translate(expr_text)
    return "{" + translated_expr + tail + "}", j + 1


# ------------------------------------------------------------
# 字符串扫描
# ------------------------------------------------------------
def _scan_string(s: str, i: int, prefix: str) -> tuple[str, int]:
    """
    扫描字符串。i 指向起始引号；prefix 为已确定的英文前缀（无则 ""）。
    返回 (输出 token, 结束下标)。
    """
    n = len(s)
    quote = s[i]
    triple = s[i:i + 3] == quote * 3
    qlen = 3 if triple else 1
    j = i + qlen
    out = [prefix, quote * qlen]
    is_raw = "r" in prefix or "R" in prefix
    is_fmt = "f" in prefix or "F" in prefix
    body_start = j

    while j < n:
        c = s[j]
        # 结束引号
        if c == quote:
            if triple:
                if s[j:j + 3] == quote * 3:
                    body = s[body_start:j]
                    out.append(body)
                    out.append(quote * 3)
                    j += 3
                    return _maybe_special("".join(out), prefix, body), j
                j += 1
                continue
            else:
                body = s[body_start:j]
                out.append(body)
                out.append(quote)
                return _maybe_special("".join(out), prefix, body), j + 1
        # 换行（非三引号非法，交给 Python 报错）
        if c == "\n" and not triple:
            out.append(s[i:j])
            return "".join(out), j
        # f-string 特有
        if is_fmt:
            if c == "{" and j + 1 < n and s[j + 1] == "{":
                out.append(s[body_start:j + 2])
                j += 2
                body_start = j
                continue
            if c == "}" and j + 1 < n and s[j + 1] == "}":
                out.append(s[body_start:j + 2])
                j += 2
                body_start = j
                continue
            if c == "{":
                out.append(s[body_start:j])
                token, j = _scan_fstring_expression(s, j + 1)
                out.append(token)
                body_start = j
                continue
        # 转义
        if c == "\\" and not is_raw and j + 1 < n:
            j += 2
            continue
        if c == "\\" and is_raw and j + 1 < n and s[j + 1] == quote:
            # 原始串中反斜杠可阻止引号结束，反斜杠保留
            j += 2
            continue
        j += 1

    # 未闭合，原样交给 Python 报错
    out.append(s[body_start:j])
    return "".join(out), j


def _maybe_special(full: str, prefix: str, body: str) -> str:
    """处理特殊字符串，如 \"__主__\" -> \"__main__\"。"""
    if not prefix and body in M.SPECIAL_STRINGS:
        return full.replace(body, M.SPECIAL_STRINGS[body], 1)
    return full


# ------------------------------------------------------------
# import 语句处理
# ------------------------------------------------------------
def _scan_import_statement(s: str, i: int) -> tuple[str, int]:
    """
    扫描整条 import / from ... import 语句（支持括号跨行、反斜杠续行）。
    i 指向「导入」或「从」的首字。返回 (原始文本, 结束下标)。
    """
    n = len(s)
    j = i
    depth = 0
    while j < n:
        c = s[j]
        if c == "#":
            k = s.find("\n", j)
            j = n if k == -1 else k
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "\n" and depth == 0:
            if j > 0 and s[j - 1] == "\\":
                j += 1
                continue
            break
        elif c == ";" and depth == 0:
            break
        j += 1
    return s[i:j], j


def _tokenize_import(code: str) -> list[tuple[str, str]]:
    toks = []
    i = 0
    n = len(code)
    simple = {".": "DOT", ",": "COMMA", "*": "STAR", "(": "LP", ")": "RP"}
    while i < n:
        c = code[i]
        if c.isspace() or c == "\\":
            i += 1
            continue
        if _is_ident_start(c):
            j = i + 1
            while j < n and _is_ident_cont(code[j]):
                j += 1
            toks.append(("NAME", code[i:j]))
            i = j
            continue
        if c in simple:
            toks.append((simple[c], c))
        i += 1
    return toks


def _split_comma(toks: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    groups = []
    cur = []
    for t in toks:
        if t[0] in ("LP", "RP"):
            continue
        if t[0] == "COMMA":
            if cur:
                groups.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        groups.append(cur)
    return groups


def _module_to_english(segs: list[str]) -> str:
    whole = ".".join(segs)
    if whole in M.MODULE_MAP:
        return M.MODULE_MAP[whole]
    return ".".join(M.MODULE_MAP.get(s, s) for s in segs)


def _import_group(g: list[tuple[str, str]]) -> str:
    segs = []
    alias = None
    p = 0
    while p < len(g):
        t = g[p]
        if t[0] == "NAME" and t[1] == "作为":
            alias = g[p + 1][1]
            break
        if t[0] == "NAME":
            segs.append(t[1])
        p += 1
    en = _module_to_english(segs)
    if alias:
        return f"import {en} as {alias}"
    if len(segs) == 1:
        cn = segs[0]
        return f"import {en}" if cn == en else f"import {en} as {cn}"
    out = [f"import {en}"]
    top_en = en.split(".")[0]
    if segs[0] != top_en:
        out.append(f"import {top_en} as {segs[0]}")
    return "\n".join(out)


def _from_name(g: list[tuple[str, str]]) -> str:
    if g and g[0][0] == "STAR":
        return "*"
    cn = g[0][1]
    en = M.ATTRIBUTE_MAP.get(cn, cn)
    alias = None
    p = 1
    while p < len(g):
        if g[p][0] == "NAME" and g[p][1] == "作为":
            alias = g[p + 1][1]
        p += 1
    if alias:
        return f"{en} as {alias}"
    if cn == en:
        return cn
    return f"{en} as {cn}"


def _convert_import(raw: str) -> str:
    """把中文 import 语句转为英文，并自动补中文别名绑定。"""
    comments = re.findall(r"#.*", raw)
    code = re.sub(r"#.*", "", raw)
    toks = _tokenize_import(code)
    if not toks:
        return raw

    first = toks[0]
    if first == ("NAME", "导入"):
        groups = _split_comma(toks[1:])
        if not groups:
            return None
        body = "\n".join(_import_group(g) for g in groups)
    elif first == ("NAME", "从"):
        p = 1
        lead = ""
        while p < len(toks) and toks[p][0] == "DOT":
            lead += "."
            p += 1
        segs = []
        # from . import x：点后直接是「导入」关键字，无模块段
        if p < len(toks) and toks[p] == ("NAME", "导入"):
            pass
        elif p < len(toks) and toks[p][0] == "NAME":
            segs.append(toks[p][1])
            p += 1
            while p < len(toks) and toks[p][0] == "DOT":
                p += 1
                if p < len(toks) and toks[p][0] == "NAME":
                    segs.append(toks[p][1])
                    p += 1
        if p < len(toks) and toks[p] == ("NAME", "导入"):
            p += 1
        else:
            return None  # 不完整的 from 语句，回退普通处理
        en_mod = _module_to_english(segs) if segs else ""
        names = [_from_name(g) for g in _split_comma(toks[p:])]
        names = [n for n in names if n]
        if not names:
            return None
        body = f"from {lead}{en_mod} import " + ", ".join(names)
    else:
        return raw

    if comments:
        bl = body.split("\n")
        bl[-1] += "  " + comments[-1]
        body = "\n".join(bl)
    return body


# ------------------------------------------------------------
# 用户定义名收集（第一遍扫描）
# ------------------------------------------------------------
def _collect_user_defined_names(source: str) -> set:
    """
    第一遍扫描：收集源码中「定义位置」出现的名字（赋值目标、def 参数与函数名、
    for 循环变量、类名、as 别名、global/nonlocal 声明、walrus 左值、复合赋值）。

    这些名字随后不再查全局内置表（如 范围/列表/长度 等 32 个常用词），
    从而避免用户变量与内置词同名时被静默改名为英文、报错无法对上中文源码。
    收集采用保守策略：宁可漏（退回内置翻译，行为一致）也不误伤引用位置。
    """
    names = set()
    n = len(source)
    i = 0
    stmt_start = True
    after_dot = False
    paren_depth = 0
    seen_def_line = False       # 本行已见过「定义」，其后的 ( 是参数区
    def_paren_depth = 0         # >0 表示当前位于 def 参数括号内（嵌套深度）
    after_eq_in_def = False     # def 参数区内刚见过 '='（默认值），其后的名字是引用
    for_collect = False         # 在「对于 ... 在」之间收集循环变量
    def_name_pending = False    # 刚见过「定义」，下一个名字是函数名
    class_name_pending = False  # 刚见过「类」，下一个名字是类名
    as_pending = False          # 刚见过「作为」，下一个名字是别名
    gl_pending = False          # 刚见过「全局」/「非局部」

    def remember(name: str) -> None:
        # 关键字、魔术方法名（__xx__）与内置常量别名（自己/本类 等）不属于
        # 用户命名空间，不收集——它们在任意位置都必须翻译
        if (
            name
            and name not in M.KEYWORD_MAP
            and name not in M.DUNDER_MAP
            and name not in M.BUILTIN_CONSTANTS
        ):
            names.add(name)

    while i < n:
        c = source[i]

        # 注释 / 字符串 / 数字：整体跳过
        if c == "#":
            j = source.find("\n", i)
            i = n if j == -1 else j
            continue
        if c in _QUOTES:
            _, i = _scan_string(source, i, "")
            continue
        if c.isdigit() or (c == "." and i + 1 < n and source[i + 1].isdigit()):
            i = _scan_number(source, i)
            continue

        # 名字
        if _is_ident_start(c) and not after_dot:
            j = i + 1
            while j < n and _is_ident_cont(source[j]):
                j += 1
            name = source[i:j]
            k = j
            while k < n and source[k] in " \t":
                k += 1
            nxt = source[k] if k < n else ""

            if name == "定义" and stmt_start:
                def_name_pending = True
                seen_def_line = True
            elif name == "类" and stmt_start:
                class_name_pending = True
            elif name == "对于" and stmt_start:
                for_collect = True
            elif name == "作为":
                as_pending = True
            elif name in ("全局", "非局部") and stmt_start:
                gl_pending = True
            elif def_name_pending:
                remember(name)
                def_name_pending = False
            elif class_name_pending:
                remember(name)
                class_name_pending = False
            elif for_collect and name == "在":
                for_collect = False
            elif for_collect:
                remember(name)
            elif as_pending:
                remember(name)
                as_pending = False
            elif gl_pending:
                remember(name)
            elif def_paren_depth == 1 and not after_eq_in_def:
                # def 参数：名字后跟 , ) = : 视为参数名（默认值 / 注解类型不收集）
                if nxt in (",", ")", "=", ":"):
                    remember(name)
            elif nxt == "=" and paren_depth == 0 and (k + 1 >= n or source[k + 1] != "="):
                remember(name)
            elif nxt in "+-" and k + 1 < n and source[k + 1] == "=":
                remember(name)  # += / -=
            elif nxt == ":" and k + 1 < n and source[k + 1] == "=":
                remember(name)  # walrus :=

            i = j
            stmt_start = False
            after_dot = False
            continue

        # 点号：属性位置的名字不参与定义收集
        if c == ".":
            after_dot = True
            i += 1
            continue

        # 其余字符
        if c == "(":
            paren_depth += 1
            if seen_def_line:
                def_paren_depth += 1
        elif c == ")":
            paren_depth = max(0, paren_depth - 1)
            if def_paren_depth > 0:
                def_paren_depth -= 1
                if def_paren_depth == 0:
                    after_eq_in_def = False
        elif c == "," and def_paren_depth == 1:
            after_eq_in_def = False
        elif c == "=" and def_paren_depth == 1:
            after_eq_in_def = True
        if c == "\n" or c == ";":
            stmt_start = True
            after_dot = False
            seen_def_line = False
            def_name_pending = False
            class_name_pending = False
            as_pending = False
            for_collect = False
            gl_pending = False
        elif c not in " \t":
            stmt_start = False
            after_dot = False
        i += 1

    return names


# ------------------------------------------------------------
# 主转译函数
# ------------------------------------------------------------
def translate(source: str) -> str:
    """将 .pycn 源码转译为标准 Python 源码。"""
    user_names = _collect_user_defined_names(source)
    n = len(source)
    out = []
    i = 0
    after_dot = False
    stmt_start = True
    paren_depth = 0

    while i < n:
        c = source[i]

        # 注释：整段复制到行尾
        if c == "#":
            j = source.find("\n", i)
            if j == -1:
                j = n
            out.append(source[i:j])
            i = j
            continue

        # 字符串
        if c in _QUOTES:
            token, i = _scan_string(source, i, "")
            out.append(token)
            after_dot = False
            stmt_start = False
            continue

        # 数字（含 .5 形式）
        if c.isdigit() or (c == "." and i + 1 < n and source[i + 1].isdigit()):
            j = _scan_number(source, i)
            out.append(source[i:j])
            i = j
            after_dot = False
            stmt_start = False
            continue

        # 名字（ASCII / 中文等 Unicode 标识符）
        if _is_ident_start(c):
            j = i + 1
            while j < n and _is_ident_cont(source[j]):
                j += 1
            name = source[i:j]

            # 语句起始的 import / from ... import：整句特殊处理
            if stmt_start and name in ("导入", "从"):
                raw, end = _scan_import_statement(source, i)
                converted_import = _convert_import(raw)
                if converted_import is not None:
                    out.append(converted_import)
                    i = end
                    after_dot = False
                    stmt_start = False
                    continue

            # 字符串前缀？（名字后跳过空白紧跟引号）
            k = j
            while k < n and source[k] in " \t":
                k += 1
            if k < n and source[k] in _QUOTES:
                prefix = _convert_prefix(name)
                if prefix is not None:
                    token, i = _scan_string(source, k, prefix)
                    # 不输出 source[j:k]：前缀与引号间的空白若在语句起始会产出非法缩进
                    out.append(token)
                    after_dot = False
                    stmt_start = False
                    continue

            # 关键字参数名：括号内「名字 = ...」（查库 API 表）
            if (
                paren_depth > 0
                and k < n
                and source[k] == "="
                and (k + 1 >= n or source[k + 1] != "=")
                and name not in M.KEYWORD_MAP
            ):
                # 用户已定义过的名字优先保留（调用自己函数的同名参数）
                if name in user_names:
                    out.append(name)
                    after_dot = False
                    stmt_start = False
                    i = j
                    continue
                # 关键字参数位置：库 API 名优先（如 键=key），再退类型方法/内置
                kw_name = M.LIBRARY_API.get(name)
                if kw_name is None:
                    kw_name = M.TYPE_METHODS.get(name)
                if kw_name is None:
                    kw_name = M.GLOBAL_NAME_MAP.get(name, name)
                out.append(kw_name)
                after_dot = False
                stmt_start = False
                i = j
                continue

            out.append(_translate_name(name, after_dot, user_names))
            after_dot = False
            stmt_start = False
            i = j
            continue

        # 点号
        if c == ".":
            out.append(".")
            after_dot = True
            stmt_start = False
            i += 1
            continue

        # 其他字符（运算符、标点、空白、换行）
        out.append(c)
        if c == "(":
            paren_depth += 1
        elif c == ")":
            paren_depth = max(0, paren_depth - 1)
        if c == "\n" or c == ";":
            stmt_start = True
            after_dot = False
        elif c not in " \t":
            stmt_start = False
            after_dot = False
        i += 1

    return "".join(out)
