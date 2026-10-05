# -*- coding: utf-8 -*-
"""PyCn 中文交互式环境（REPL）。"""
import code
import sys

from .translator import translate
from .importer import install as install_import_hook

BANNER = (
    "PyCn 交互式环境  (全中文 Python；输入 退出() 或按 Ctrl+Z 回车退出)\n"
)


class PycnConsole:
    def __init__(self):
        install_import_hook()
        self.buffer: list[str] = []
        self.globals = {
            "__name__": "__main__",
            "__builtins__": __builtins__,
        }

    def push(self, line: str) -> bool:
        """喂入一行原始输入，返回 True 表示需要更多行。"""
        self.buffer.append(line)
        source = "\n".join(self.buffer) + "\n"
        translated = translate(source)
        try:
            code_obj = code.compile_command(translated, "<pycn交互>", "single")
        except (OverflowError, SyntaxError, ValueError):
            self.buffer = []
            self.show_syntax_error(translated)
            return False
        if code_obj is None:
            return True  # 语句不完整
        self.buffer = []
        try:
            exec(code_obj, self.globals)
        except SystemExit:
            raise
        except BaseException:
            import traceback
            traceback.print_exc()
        return False

    @staticmethod
    def show_syntax_error(translated: str):
        import traceback
        # 用转译后的源码重建语法错误信息（行号与中文输入一致）
        try:
            compile(translated, "<pycn交互>", "single")
        except BaseException:
            traceback.print_exc()

    def interact(self):
        print(BANNER)
        more = False
        while True:
            prompt = "... " if more else "pycn> "
            try:
                line = input(prompt)
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print("\n当前输入已取消")
                self.buffer = []
                more = False
                continue
            more = self.push(line)


def run_repl() -> int:
    PycnConsole().interact()
    return 0
