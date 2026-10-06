# PyCn JetBrains 插件

适用于 IntelliJ IDEA、PyCharm、WebStorm、GoLand 等 JetBrains IDE（基于 2024.2 构建，兼容 242–251）。

功能：

- `.pycn` 文件类型识别与图标
- 中文关键字 / 内置函数 / 异常 / 字符串 / 数字语法高亮（可在 Settings | Editor | Color Scheme | PyCn 自定义）
- New 菜单中的 PyCn 文件模板
- 专用「PyCn」运行配置，一键运行 `.pycn`

## 构建要求

- **JDK 17**（Gradle toolchain；JDK 8 无法构建本插件）
- 网络（首次构建需下载 IntelliJ Platform SDK）

## 构建

```bash
# Windows
gradlew.bat buildPlugin

# macOS / Linux
./gradlew buildPlugin
```

产物位于 `build/distributions/pycn-jetbrains-plugin-0.1.0.zip`。

## 安装

1. `File | Settings | Plugins | ⚙ | Install Plugin from Disk...`
2. 选择上面的 zip，重启 IDE。

## 运行程序

方式一：打开 `.pycn` 文件，选择运行配置下拉框 → Edit Configurations → + → PyCn，指定脚本路径后运行。

方式二：在 IDE 内置 Terminal 中执行：

```bash
python -m pycn_lang run 文件.pycn
```

默认运行方式为 `python -m pycn_lang run`；若已把 `pycn` 加入 PATH，可在配置中勾选使用 `pycn` 命令。
