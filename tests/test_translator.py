# -*- coding: utf-8 -*-
"""PyCn 转译器单元测试。"""
import unittest

from pycn_lang.translator import translate
from pycn_lang import mappings as M


class TestKeywords(unittest.TestCase):
    def test_all_keywords_mapped(self):
        for zh, en in M.KEYWORD_MAP.items():
            self.assertEqual(translate(zh), en)

    def test_control_flow(self):
        src = "对于 名字 在 名单:\n    如果 名字:\n        跳出\n    否则:\n        继续\n"
        out = translate(src)
        self.assertIn("for 名字 in 名单:", out)
        self.assertIn("if 名字:", out)
        self.assertIn("break", out)
        self.assertIn("else:", out)
        self.assertIn("continue", out)

    def test_boolean_and_none(self):
        self.assertEqual(translate("真"), "True")
        self.assertEqual(translate("假"), "False")
        self.assertEqual(translate("空"), "None")

    def test_logical_operators(self):
        self.assertEqual(translate("a 且 b 或 非 c"), "a and b or not c")

    def test_while(self):
        self.assertIn("while x > 0:", translate("当 x > 0:"))

    def test_lambda(self):
        self.assertEqual(translate("匿名 x: x + 1"), "lambda x: x + 1")

    def test_match_case(self):
        src = "匹配 状态:\n    情形 200:\n        跳过\n    情形 _:\n        抛出 值错误()\n"
        out = translate(src)
        self.assertIn("match 状态:", out)
        self.assertIn("case 200:", out)
        self.assertIn("pass", out)
        self.assertIn("case _:", out)
        self.assertIn("raise ValueError()", out)


class TestBuiltins(unittest.TestCase):
    def test_print(self):
        self.assertEqual(translate('打印("你好")'), 'print("你好")')

    def test_print_kwargs(self):
        out = translate('打印("a", "b", 分隔="-", 结尾="", 立即刷新=真)')
        self.assertEqual(out, 'print("a", "b", sep="-", end="", flush=True)')
        self.assertEqual(translate('打印(内容, 文件=日志)'), "print(内容, file=日志)")

    def test_len_range(self):
        self.assertEqual(translate("长度(范围(10))"), "len(range(10))")

    def test_type_conversion(self):
        self.assertEqual(translate("整数(x)"), "int(x)")
        self.assertEqual(translate("字符串(x)"), "str(x)")
        self.assertEqual(translate("列表(x)"), "list(x)")

    def test_collection_constructors(self):
        self.assertEqual(translate("字典()"), "dict()")
        self.assertEqual(translate("元组()"), "tuple()")
        self.assertEqual(translate("集合()"), "set()")
        self.assertEqual(translate("冻结集合()"), "frozenset()")

    def test_exceptions_global(self):
        self.assertEqual(translate("值错误"), "ValueError")
        self.assertEqual(translate("键错误"), "KeyError")
        self.assertEqual(translate("文件未找到错误"), "FileNotFoundError")

    def test_ellipsis_constant(self):
        self.assertEqual(translate("省略号"), "Ellipsis")


class TestUserDefinedNames(unittest.TestCase):
    def test_chinese_function_name_preserved(self):
        src = "定义 阶乘(数):\n    返回 数\n"
        out = translate(src)
        self.assertIn("def 阶乘(数):", out)
        self.assertIn("return 数", out)

    def test_chinese_variable_score_preserved(self):
        # 「分数」是 fractions 模块的中文名，但作为变量必须保留
        out = translate("分数 = 90\n")
        self.assertEqual(out, "分数 = 90\n")

    def test_mixed_name_preserved(self):
        out = translate("我的变量2 = 1\n")
        self.assertIn("我的变量2 = 1", out)

    def test_builtin_word_as_assignment_target(self):
        # 用户把内置词当变量名：定义与引用都应保留中文，不再翻译成英文内置名
        src = "范围 = 10\n打印(范围)\n"
        out = translate(src)
        self.assertIn("范围 = 10", out)
        self.assertIn("print(范围)", out)

    def test_builtin_word_as_for_variable(self):
        src = "对于 长度 在 范围(3):\n    打印(长度)\n"
        out = translate(src)
        self.assertIn("for 长度 in range(3):", out)
        self.assertIn("print(长度)", out)

    def test_builtin_word_as_function_param(self):
        src = "定义 统计(长度):\n    返回 长度\n"
        out = translate(src)
        self.assertEqual(out, "def 统计(长度):\n    return 长度\n")

    def test_builtin_word_as_class_name(self):
        self.assertEqual(translate("类 列表:\n    跳过\n"), "class 列表:\n    pass\n")

    def test_builtin_word_as_alias(self):
        self.assertEqual(
            translate("伴随 打开('f') 作为 文件:\n    跳过\n"),
            "with open('f') as 文件:\n    pass\n",
        )

    def test_builtin_word_as_global_decl(self):
        self.assertEqual(
            translate("全局 长度\n长度 = 3\n"),
            "global 长度\n长度 = 3\n",
        )


class TestAttributes(unittest.TestCase):
    def test_list_methods(self):
        out = translate("名单.追加(1)")
        self.assertEqual(out, "名单.append(1)")
        self.assertEqual(translate("名单.弹出()"), "名单.pop()")
        self.assertEqual(translate("名单.原地排序()"), "名单.sort()")
        self.assertEqual(translate("名单.反转()"), "名单.reverse()")

    def test_dict_methods(self):
        self.assertEqual(translate("映射表.键()"), "映射表.keys()")
        self.assertEqual(translate("映射表.项()"), "映射表.items()")
        self.assertEqual(translate("映射表.获取('k')"), "映射表.get('k')")

    def test_str_methods(self):
        self.assertEqual(translate('s.分割(",")'), 's.split(",")')
        self.assertEqual(translate("s.去除()"), "s.strip()")
        self.assertEqual(translate("s.替换('a','b')"), "s.replace('a','b')")
        self.assertEqual(translate("s.开头是('a')"), "s.startswith('a')")

    def test_file_methods(self):
        self.assertEqual(translate("f.读取()"), "f.read()")
        self.assertEqual(translate("f.写入(x)"), "f.write(x)")
        self.assertEqual(translate("f.关闭()"), "f.close()")

    def test_library_attribute_api(self):
        self.assertEqual(translate("数学.平方根(2)"), "数学.sqrt(2)")
        self.assertEqual(translate("随机.随机小数()"), "随机.random()")

    def test_keyword_after_dot_preserved(self):
        # 点号后的关键字不再翻译：x.真 保持原样，而不是产出非法的 x.True
        self.assertEqual(translate("x.真"), "x.真")
        self.assertEqual(translate("x.空"), "x.空")
        self.assertEqual(translate("对象.长度"), "对象.长度")

    def test_attribute_method_still_translated(self):
        self.assertEqual(translate("名单.追加(1)"), "名单.append(1)")


class TestDunder(unittest.TestCase):
    def test_dunder_init(self):
        out = translate("定义 __初始化__(自己):\n    跳过\n")
        self.assertIn("def __init__(self):", out)

    def test_dunder_str(self):
        out = translate("定义 __字符串__(自己):\n    返回 ''\n")
        self.assertIn("def __str__(self):", out)

    def test_dunder_getitem(self):
        self.assertEqual(translate("__获取项__"), "__getitem__")

    def test_name_main(self):
        out = translate('如果 __名字__ == "__主__":\n    跳过\n')
        self.assertIn('if __name__ == "__main__":', out)


class TestStrings(unittest.TestCase):
    def test_comment_preserved(self):
        out = translate("# 这是注释 打印\n打印(1)\n")
        self.assertIn("# 这是注释 打印", out)

    def test_string_content_untouched(self):
        out = translate('打印("如果 否则 打印")')
        self.assertEqual(out, 'print("如果 否则 打印")')

    def test_raw_prefix(self):
        out = translate('原"\\n"')
        self.assertEqual(out, 'r"\\n"')

    def test_bytes_prefix(self):
        self.assertEqual(translate('字"abc"'), 'b"abc"')

    def test_triple_string(self):
        out = translate('"""如果 打印"""\n')
        self.assertIn('"""如果 打印"""', out)

    def test_escape_quote(self):
        out = translate("'a\\'b'")
        self.assertEqual(out, "'a\\'b'")

    def test_fstring_expression(self):
        out = translate('格"x={x}"')
        self.assertEqual(out, 'f"x={x}"')

    def test_fstring_chinese_expression(self):
        out = translate('格"和={自己.名字}"')
        self.assertEqual(out, 'f"和={self.名字}"')

    def test_fstring_conversion(self):
        out = translate('格"{x!表示}"')
        self.assertEqual(out, 'f"{x!r}"')
        out = translate('格"{x!字符串}"')
        self.assertEqual(out, 'f"{x!s}"')

    def test_fstring_format_spec(self):
        out = translate('格"{x:.2f}"')
        self.assertEqual(out, 'f"{x:.2f}"')

    def test_fstring_escaped_braces(self):
        out = translate('格"{{不是表达式}}"')
        self.assertEqual(out, 'f"{{不是表达式}}"')

    def test_prefix_with_space(self):
        # 中文前缀与引号之间有空格：不得产出非法缩进
        self.assertEqual(translate('格 "x={1}"'), 'f"x={1}"')
        self.assertEqual(translate('原 "a"'), 'r"a"')
        self.assertEqual(translate('字 "a"'), 'b"a"')
        out = translate("如果 真:\n    格\"x={1}\"\n")
        self.assertIn("    f\"x={1}\"", out)

    def test_unclosed_fstring(self):
        # 未闭合花括号：原样交给 Python 报出正确位置的 SyntaxError
        out = translate('格"{"')
        self.assertEqual(out, 'f"{"')
        with self.assertRaises(SyntaxError):
            compile(out, "<test>", "exec")

    def test_fstring_prefix_combined(self):
        self.assertEqual(translate('格原"a"'), 'fr"a"')

    def test_english_u_prefix_not_supported(self):
        # u 前缀已从 Python 移除：不再被当作合法字符串前缀
        out = translate('u"abc"')
        self.assertEqual(out, 'u"abc"')


class TestImport(unittest.TestCase):
    def test_import_module(self):
        self.assertEqual(translate("导入 数学\n"), "import math as 数学\n")

    def test_import_module_as_alias(self):
        out = translate("导入 数学 作为 数\n")
        self.assertEqual(out, "import math as 数\n")

    def test_import_multiple(self):
        out = translate("导入 数学, 随机\n")
        self.assertEqual(out, "import math as 数学\nimport random as 随机\n")

    def test_from_import(self):
        out = translate("从 数学 导入 平方根\n")
        self.assertEqual(out, "from math import sqrt as 平方根\n")

    def test_from_import_multiple(self):
        out = translate("从 数学 导入 平方根, 正弦\n")
        self.assertEqual(out, "from math import sqrt as 平方根, sin as 正弦\n")

    def test_from_import_alias(self):
        out = translate("从 数学 导入 平方根 作为 开方\n")
        self.assertEqual(out, "from math import sqrt as 开方\n")

    def test_relative_import(self):
        out = translate("从 . 导入 工具\n")
        self.assertEqual(out, "from . import 工具\n")

    def test_relative_parent(self):
        out = translate("从 .. 导入 工具\n")
        self.assertEqual(out, "from .. import 工具\n")

    def test_import_star(self):
        out = translate("从 数学 导入 *\n")
        self.assertEqual(out, "from math import *\n")

    def test_import_english_name_preserved(self):
        # 用户导入自己模块（英文/未登记名）
        out = translate("导入 我的模块\n")
        self.assertEqual(out, "import 我的模块\n")

    def test_parenthesized_import(self):
        out = translate("从 数学 导入 (平方根, 正弦)\n")
        self.assertEqual(out, "from math import sqrt as 平方根, sin as 正弦\n")

    def test_typing_import(self):
        out = translate("从 类型注解 导入 任意, 可选\n")
        self.assertEqual(out, "from typing import Any as 任意, Optional as 可选\n")

    def test_submodule_import(self):
        out = translate("从 网址解析 导入 解析网址\n")
        self.assertEqual(out, "from urllib.parse import urlparse as 解析网址\n")


class TestMisc(unittest.TestCase):
    def test_line_count_preserved(self):
        src = "打印(1)\n打印(2)\n打印(3)\n"
        out = translate(src)
        self.assertEqual(out.count("\n"), src.count("\n"))

    def test_walrus(self):
        out = translate("如果 (n := 长度(x)):\n    跳过\n")
        self.assertIn("(n := len(x))", out)

    def test_augmented_assign(self):
        out = translate("x += 1\n")
        self.assertIn("x += 1", out)

    def test_decorator(self):
        out = translate("@静态方法\ndef f():\n    pass\n")
        self.assertIn("@staticmethod", out)

    def test_semicolon(self):
        out = translate("x = 1; 打印(x)\n")
        self.assertIn("x = 1;", out)
        self.assertIn("print(x)", out)

    def test_try_except_finally(self):
        src = "尝试:\n    跳过\n捕获 值错误 作为 e:\n    跳过\n最终:\n    跳过\n"
        out = translate(src)
        self.assertIn("try:", out)
        self.assertIn("except ValueError as e:", out)
        self.assertIn("finally:", out)

    def test_with(self):
        out = translate('伴随 打开("f") 作为 f:\n    f.读取()\n')
        self.assertIn('with open("f") as f:', out)

    def test_async_await(self):
        out = translate("异步 定义 f():\n    等待 g()\n")
        self.assertIn("async def f():", out)
        self.assertIn("await g()", out)

    def test_yield(self):
        self.assertEqual(translate("生成 x"), "yield x")
        self.assertEqual(translate("生成 来自 x"), "yield from x")

    def test_assert_del_global(self):
        self.assertEqual(translate("断言 x"), "assert x")
        self.assertEqual(translate("删除 x"), "del x")
        self.assertEqual(translate("全局 x"), "global x")
        self.assertEqual(translate("非局部 x"), "nonlocal x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
