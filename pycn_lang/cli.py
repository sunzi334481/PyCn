# -*- coding: utf-8 -*-
"""
PyCn 命令行工具。

用法：
  pycn run 脚本.pycn [参数 ...]    运行 .pycn 程序
  pycn 脚本.pycn [参数 ...]        run 的简写
  pycn compile 脚本.pycn [-o 输出.py]
                                   把 .pycn 转译为标准 Python
  pycn repl                        启动中文交互式环境
  pycn version                     显示版本
"""
import argparse
import sys
from pathlib import Path

from . import __version__
from .translator import translate
from .importer import install as install_import_hook


def _read_source(path: Path) -> str:
    try:
        # utf-8-sig：兼容记事本等工具保存时附带的 BOM
        return path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"错误：找不到文件 {path}", file=sys.stderr)
        raise SystemExit(2)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"错误：无法读取 {path}（{exc}）", file=sys.stderr)
        raise SystemExit(2)


def cmd_run(script: str, script_args: list[str]) -> int:
    path = Path(script).resolve()
    if not path.is_file():
        print(f"错误：找不到文件 {path}", file=sys.stderr)
        return 2
    if path.suffix != ".pycn":
        print(f"警告：{path.name} 不是 .pycn 文件，仍尝试按 PyCn 解析", file=sys.stderr)

    install_import_hook()

    # 模拟 Python：脚本目录置于模块搜索路径首位
    script_dir = str(path.parent)
    old_argv = sys.argv
    path_snapshot = list(sys.path)
    if script_dir in sys.path:
        sys.path.remove(script_dir)
    sys.path.insert(0, script_dir)
    sys.argv = [str(path)] + script_args

    try:
        source = _read_source(path)
        translated = translate(source)
        try:
            code_obj = compile(translated, str(path), "exec")
        except SyntaxError as exc:
            # 转译后语法错误（通常是源码语法问题），直接展示
            print(f"语法错误：{exc}", file=sys.stderr)
            return 1

        module_globals = {
            "__name__": "__main__",
            "__file__": str(path),
            "__builtins__": __builtins__,
        }
        try:
            exec(code_obj, module_globals)
        except SystemExit as exc:
            code = exc.code
            return int(code) if isinstance(code, int) else (0 if code is None else 1)
        except KeyboardInterrupt:
            print("\n键盘中断", file=sys.stderr)
            return 130
        except Exception as exc:
            # 剥掉本函数内部帧，traceback 从 .pycn 源码开始展示
            import traceback
            tb = exc.__traceback__
            if tb is not None:
                tb = tb.tb_next
            traceback.print_exception(type(exc), exc, tb)
            return 1
        return 0
    finally:
        sys.path[:] = path_snapshot
        sys.argv = old_argv


def cmd_compile(script: str, output: str | None) -> int:
    path = Path(script).resolve()
    if not path.is_file():
        print(f"错误：找不到文件 {path}", file=sys.stderr)
        return 2
    if path.suffix != ".pycn":
        print(f"警告：{path.name} 不是 .pycn 文件，仍尝试按 PyCn 解析", file=sys.stderr)
    source = _read_source(path)
    translated = translate(source)
    header = "# -*- coding: utf-8 -*-\n# 本文件由 PyCn 自动转译生成，原始文件：{}\n\n".format(path.name)
    result = header + translated

    if output is None:
        out_path = path.with_suffix(".py")
        try:
            out_path.write_text(result, encoding="utf-8")
        except OSError as exc:
            print(f"错误：无法写入 {out_path}（{exc}）", file=sys.stderr)
            return 1
        print(f"已生成 {out_path}")
    elif output == "-":
        sys.stdout.write(result)
    else:
        try:
            Path(output).write_text(result, encoding="utf-8")
        except OSError as exc:
            print(f"错误：无法写入 {output}（{exc}）", file=sys.stderr)
            return 1
        print(f"已生成 {output}")
    return 0


def cmd_repl() -> int:
    from .repl import run_repl
    return run_repl()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pycn",
        description="PyCn —— 全中文语法的 Python 编程语言",
    )
    parser.add_argument("--version", action="version", version=f"PyCn {__version__}")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="运行 .pycn 程序")
    p_run.add_argument("script", help=".pycn 脚本路径")
    p_run.add_argument("args", nargs=argparse.REMAINDER, help="传递给脚本的参数")

    p_compile = sub.add_parser("compile", help="转译为标准 Python")
    p_compile.add_argument("script", help=".pycn 脚本路径")
    p_compile.add_argument("-o", "--output", default=None,
                           help="输出路径；- 表示标准输出；默认为同名 .py")

    sub.add_parser("repl", help="启动交互式环境")
    sub.add_parser("version", help="显示版本")

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # 简写：pycn 脚本.pycn ...
    if argv and argv[0] not in ("run", "compile", "repl", "version", "-h", "--help", "--version"):
        argv = ["run"] + argv

    parser = build_parser()
    ns = parser.parse_args(argv)

    if ns.command == "run":
        return cmd_run(ns.script, ns.args)
    if ns.command == "compile":
        return cmd_compile(ns.script, ns.output)
    if ns.command == "repl":
        return cmd_repl()
    if ns.command == "version":
        print(f"PyCn {__version__}")
        return 0

    parser.print_help()
    return 0
