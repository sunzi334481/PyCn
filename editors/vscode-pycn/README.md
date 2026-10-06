# PyCn VSCode 扩展

为 PyCn 语言（`.pycn`，全中文语法的 Python）提供：

- `.pycn` 文件识别
- 中文关键字 / 内置函数 / 异常 / 字符串 / f-string 语法高亮
- 中文代码片段（定义、类、如果否则、对于、尝试捕获、伴随、匹配等）
- 一键运行（编辑器右上角运行按钮 / 右键菜单 / `Ctrl+Alt+N`）

## 前置条件

先安装 PyCn 语言本体（在项目根目录）：

```bash
pip install -e .
```

## 安装扩展

方式一（VSIX）：用 `vsce package` 生成 `pycn-vscode.vsix`，然后：

```bash
code --install-extension pycn-vscode.vsix
```

方式二（开发模式）：把本目录复制到 `~/.vscode/extensions/pycn-0.1.0`，重启 VSCode。

## 运行程序

打开任意 `.pycn` 文件，点击编辑器右上角的 ▶ 按钮，或按 `Ctrl+Alt+N`。
扩展默认使用 `python -m pycn_lang run` 运行；若已把 `pycn` 加入 PATH，
可在设置 `pycn.runner` 中切换为 `pycn`。
