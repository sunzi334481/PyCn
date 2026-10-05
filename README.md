# PyCn —— 全中文语法的 Python

> 用中文写 Python：所有非用户自定义的语法都是中文，源码后缀 `.pycn`，VSCode / JetBrains IDE / Visual Studio 均可直接运行。

PyCn 是一门**中文语法编程语言**，它把 Python 的语法逐词翻译成中文（`打印` = `print`、`定义` = `def`、`如果` = `if`……），底层仍是标准 Python 3：源码被转译为 Python 后执行，行为完全一致，天然兼容整个 Python 生态。

```pycn
# 你好，世界
打印("你好，PyCn！")

定义 阶乘(数):
    如果 数 <= 1:
        返回 1
    返回 数 * 阶乘(数 - 1)

打印("5 的阶乘 =", 阶乘(5))
```

```bash
$ python -m pycn_lang run 你好.pycn
你好，PyCn！
5 的阶乘 = 120
```

## 特性

- **全中文语法**：39 个关键字、60+ 内置函数、70+ 异常、80+ 标准库模块、约 500 个标准库 API 全部中文化；
- **用户代码不被误伤**：自定义的中文变量名 / 函数名 / 类名原样保留（Python 3 原生支持 Unicode 标识符），转译分「关键字 → 属性位置 → 全局名字」三级查表；
- **与 Python 逐词对应**：任何 PyCn 代码都可 `compile` 转回可读 Python，报错行号与源码一致，traceback 直接显示 `.pycn` 中文行；
- **预装标准库**：math、random、datetime、json、re、os、threading、asyncio、sqlite3、turtle 等直接 `导入 数学` 使用；
- **中文 f-string / 原始串 / 字节串**：`格"..."`、`原"..."`、`字"..."`；
- **多文件工程**：`.pycn` 文件可互相导入（自带 import 钩子）；
- **三大编辑器支持**：VSCode（已打包安装验证）、JetBrains IDE（源码工程）、Visual Studio（源码工程）。

## 目录结构

```
pycn/
├── pycn_lang/              # 语言核心
│   ├── mappings.py         # 全部中文映射（唯一事实来源）
│   ├── translator.py       # token 级转译器
│   ├── importer.py         # .pycn 模块导入钩子
│   ├── cli.py              # 命令行 run / compile / repl / version
│   └── repl.py             # 中文交互式环境
├── docs/
│   ├── 语言手册.md          # 语法完整说明（本项目的入门文档）
│   └── 基础库与预装库.md    # 全部内置与标准库 API 清单（由 tools/gen_api_docs.py 自动生成）
├── tools/
│   └── gen_api_docs.py     # 从 mappings.py 生成基础库文档
├── examples/               # 8 个可运行示例
├── tests/                  # 72 个回归测试
└── editors/
    ├── vscode-pycn/        # VSCode 扩展（已打包 pycn-vscode.vsix）
    ├── jetbrains-pycn/     # JetBrains 插件源码（IDEA/PyCharm 等）
    └── visualstudio-pycn/  # Visual Studio 插件源码
```

## 安装

需要 **Python 3.10+**（开发环境为 3.14）。

```bash
cd pycn
pip install -e .
```

安装后获得 `pycn` 命令：

```bash
pycn --version
```

> 提示：若 `pycn.exe` 不在 PATH 中（例如安装在用户级 Scripts 目录），统一改用 `python -m pycn_lang`，效果相同。

## 使用

```bash
# 运行 .pycn 程序
python -m pycn_lang run examples/冒烟测试.pycn

# run 的简写
python -m pycn_lang examples/冒烟测试.pycn

# 转译为标准 Python（默认生成同名 .py；-o - 打印到屏幕）
python -m pycn_lang compile examples/冒烟测试.pycn -o -

# 中文交互式环境
python -m pycn_lang repl

# 版本
python -m pycn_lang version
```

交互式环境示例：

```
>>> 打印("你好")
你好
>>> 定义 平方(数): 返回 数 * 数
>>> 平方(7)
49
```

## 文档

| 文档 | 内容 |
| --- | --- |
| [docs/语言手册.md](docs/语言手册.md) | 语法、关键字、字符串前缀、import、CLI、原理与边界 |
| [docs/基础库与预装库.md](docs/基础库与预装库.md) | 全部中文内置与标准库 API 清单（与实现自动同步） |

## 编辑器插件

### VSCode（推荐，已安装验证）

1. 安装扩展：`code --install-extension editors/vscode-pycn/pycn-vscode.vsix`
2. 打开任意 `.pycn` 文件，获得语法高亮、代码片段、注释切换；
3. 点击编辑器右上角 **▶** 按钮（或右键 → 运行 PyCn、快捷键 `Ctrl+Alt+N`）直接运行，输出显示在终端；
4. 可配置 `pycn.pythonPath`（Python 解释器路径）与 `pycn.runner`（运行命令，默认 `python -m pycn_lang run`）。

### JetBrains IDE（IDEA / PyCharm 等）

插件源码位于 `editors/jetbrains-pycn/`（IntelliJ Platform Plugin，Kotlin）。构建需要 **JDK 17**：

```bash
cd editors/jetbrains-pycn
./gradlew buildPlugin    # 产物在 build/libs/*.jar
```

然后：Settings → Plugins → ⚙ → Install Plugin from Disk… 选择 jar。功能：`.pycn` 识别、语法高亮、一键运行（运行配置，默认 `python -m pycn_lang run`）。

### Visual Studio

插件源码位于 `editors/visualstudio-pycn/`（纯 MEF 扩展：语法高亮 + 编辑器顶部「▶ 运行 PyCn」按钮）。在装有 VSSDK 的环境用 VS 打开 `PycnVsPackage/PycnVsPackage.csproj` 构建并安装即可。

## 测试

```bash
cd pycn
python -m unittest discover -s tests
```

72 个用例全部通过：映射完整性、转译正确性、import 钩子、端到端运行。

## 示例速览

```pycn
# 标准库：数学 / 随机 / 日期时间 / JSON / 正则 / 操作系统
导入 数学
打印("根号 16 =", 数学.平方根(16))          # 4.0

导入 随机
随机.设置种子(42)
打印("随机整数 [1,100]：", 随机.随机整数(1, 100))

从 日期时间 导入 日期时间类
现在 = 日期时间类.现在()
打印("今年是：", 现在.年)

导入 序列化
文本 = 序列化.转文本({"名字": "PyCn"}, 确保ASCII=假, 缩进=2)

导入 正则
匹配 = 正则.搜索(r"1[3-9]\d{9}", "电话：13800138000")
如果 匹配:
    打印("找到手机号：", 匹配.分组())

导入 操作系统
打印("当前目录：", 操作系统.当前目录())
```

更多示例见 `examples/` 目录，每个文件顶部有注释说明覆盖点。

## 许可

MIT License。
