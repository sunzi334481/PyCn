package com.pycn.plugin

import com.intellij.lexer.LexerBase
import com.intellij.psi.tree.IElementType

/**
 * PyCn 手写词法分析器。关键字 / 内置函数 / 异常集合与 pycn_lang/mappings.py 保持一致。
 */
class PycnLexer : LexerBase() {

    private lateinit var buffer: CharSequence
    private var startOffset = 0
    private var endOffset = 0
    private var tokenStart = 0
    private var tokenEnd = 0
    private var myTokenType: IElementType? = null

    override fun start(buffer: CharSequence, startOffset: Int, endOffset: Int, initialState: Int) {
        this.buffer = buffer
        this.startOffset = startOffset
        this.endOffset = endOffset
        this.tokenStart = startOffset
        this.tokenEnd = startOffset
        advance()
    }

    override fun getState(): Int = 0
    override fun getTokenType(): IElementType? = myTokenType
    override fun getTokenStart(): Int = tokenStart
    override fun getTokenEnd(): Int = tokenEnd
    override fun getBufferSequence(): CharSequence = buffer
    override fun getBufferEnd(): Int = endOffset

    override fun advance() {
        tokenStart = tokenEnd
        if (tokenStart >= endOffset) {
            myTokenType = null
            return
        }
        val c = buffer[tokenStart]
        when {
            c.isWhitespace() -> scanWhitespace()
            c == '#' -> scanComment()
            c == '"' || c == '\'' -> scanQuoted(tokenStart)
            isPrefixChar(c) && quoteAfterPrefix() -> scanPrefixed()
            c.isDigit() || (c == '.' && tokenStart + 1 < endOffset && buffer[tokenStart + 1].isDigit()) ->
                scanNumber()
            isIdentStart(c) -> scanName()
            else -> scanOperatorOrPunct()
        }
    }

    // ----------------------------------------------------------
    private fun scanWhitespace() {
        var j = tokenStart + 1
        while (j < endOffset && buffer[j].isWhitespace()) j++
        myTokenType = PycnTokenTypes.空白
        tokenEnd = j
    }

    private fun scanComment() {
        var j = tokenStart + 1
        while (j < endOffset && buffer[j] != '\n') j++
        myTokenType = PycnTokenTypes.注释
        tokenEnd = j
    }

    private fun scanName() {
        var j = tokenStart + 1
        while (j < endOffset && isIdentCont(buffer[j])) j++
        val name = buffer.substring(tokenStart, j)
        myTokenType = when {
            name in KEYWORDS -> PycnTokenTypes.关键字
            name in BUILTINS -> PycnTokenTypes.内置函数
            name in EXCEPTIONS -> PycnTokenTypes.异常名
            else -> PycnTokenTypes.名字
        }
        tokenEnd = j
    }

    private fun scanNumber() {
        var j = tokenStart
        if (buffer[j] == '0' && j + 1 < endOffset && buffer[j + 1] in "xXoObB") {
            j += 2
            while (j < endOffset && (buffer[j].isLetterOrDigit() || buffer[j] == '_')) j++
        } else {
            while (j < endOffset && (buffer[j].isDigit() || buffer[j] == '_')) j++
            if (j < endOffset && buffer[j] == '.' && (j + 1 >= endOffset || buffer[j + 1] != '.')) {
                j++
                while (j < endOffset && (buffer[j].isDigit() || buffer[j] == '_')) j++
            }
            if (j < endOffset && buffer[j] in "eE") {
                var k = j + 1
                if (k < endOffset && buffer[k] in "+-") k++
                if (k < endOffset && buffer[k].isDigit()) {
                    j = k
                    while (j < endOffset && (buffer[j].isDigit() || buffer[j] == '_')) j++
                }
            }
            if (j < endOffset && buffer[j] in "jJ") j++
        }
        myTokenType = PycnTokenTypes.数字
        tokenEnd = j
    }

    // ----------------------------------------------------------
    private fun isPrefixChar(c: Char): Boolean = c in "格原字frbFRBU"

    private fun quoteAfterPrefix(): Boolean {
        var j = tokenStart
        while (j < endOffset && buffer[j] in "格原字frbFRBU") j++
        while (j < endOffset && buffer[j] in " \t") j++
        return j < endOffset && (buffer[j] == '"' || buffer[j] == '\'')
    }

    private fun scanPrefixed() {
        var j = tokenStart
        while (j < endOffset && buffer[j] in "格原字frbFRBU") j++
        val prefix = buffer.substring(tokenStart, j)
        val raw = prefix.any { it == 'r' || it == 'R' || it == '原' }
        while (j < endOffset && buffer[j] in " \t") j++
        scanQuoted(j, raw)
    }

    private fun scanQuoted(from: Int, raw: Boolean = false) {
        val quote = buffer[from]
        val triple = from + 2 < endOffset && buffer[from + 1] == quote && buffer[from + 2] == quote
        val qlen = if (triple) 3 else 1
        var j = from + qlen
        while (j < endOffset) {
            val c = buffer[j]
            if (c == quote) {
                if (triple) {
                    if (j + 2 < endOffset && buffer[j + 1] == quote && buffer[j + 2] == quote) {
                        j += 3
                        break
                    }
                    j++
                } else {
                    j++
                    break
                }
            }
            if (c == '\n' && !triple) break
            if (c == '\\') {
                if (raw) {
                    if (j + 1 < endOffset && buffer[j + 1] == quote) j += 2 else j++
                } else {
                    j += 2
                }
                continue
            }
            j++
        }
        myTokenType = PycnTokenTypes.字符串
        tokenEnd = j
    }

    // ----------------------------------------------------------
    private fun scanOperatorOrPunct() {
        val c = buffer[tokenStart]
        if (c in PUNCTUATION) {
            myTokenType = PycnTokenTypes.标点
            tokenEnd = tokenStart + 1
            return
        }
        for (op in OPERATORS) {
            if (tokenStart + op.length <= endOffset &&
                buffer.substring(tokenStart, tokenStart + op.length) == op
            ) {
                myTokenType = PycnTokenTypes.运算符
                tokenEnd = tokenStart + op.length
                return
            }
        }
        myTokenType = PycnTokenTypes.标点
        tokenEnd = tokenStart + 1
    }

    companion object {
        private fun isIdentStart(c: Char) = c == '_' || c.isLetter()
        private fun isIdentCont(c: Char) = c == '_' || c.isLetterOrDigit()

        val KEYWORDS = setOf(
            "如果", "否则若", "否则", "对于", "在", "当", "跳出", "继续",
            "返回", "生成", "来自", "匹配", "情形", "是", "尝试", "捕获",
            "最终", "抛出", "导入", "从", "作为", "伴随", "断言", "删除",
            "全局", "非局部", "异步", "等待", "跳过", "匿名", "且", "或",
            "非", "不在", "不是", "真", "假", "空"
        )

        val BUILTINS = setOf(
            "打印", "输入", "长度", "范围", "整数", "浮点", "复数", "字符串",
            "布尔", "列表", "字典", "元组", "集合", "冻结集合", "字节", "字节数组",
            "内存视图", "类型", "是实例", "是子类", "有属性", "取属性", "设属性", "删属性",
            "超类", "属性", "静态方法", "类方法", "绝对值", "最小值", "最大值", "求和",
            "排序", "反序", "枚举", "打包", "映射", "过滤", "任一", "全部",
            "四舍五入", "商余", "幂", "字符", "序号", "十六进制", "二进制", "八进制",
            "可迭代", "下一个", "切片", "打开", "求值", "执行", "编译", "帮助",
            "目录", "标识", "哈希", "表示", "变量", "全局变量", "局部变量", "断点",
            "退出"
        )

        val EXCEPTIONS = setOf(
            "根异常", "异常", "系统退出", "键盘中断", "生成器退出", "停止迭代", "停止异步迭代", "算术错误",
            "零除错误", "溢出错误", "浮点错误", "断言错误", "属性错误", "缓冲错误", "末尾错误", "导入错误",
            "模块未找到错误", "查找错误", "索引错误", "键错误", "名称错误", "未绑定局部错误", "环境错误", "阻塞错误",
            "子进程错误", "连接错误", "连接断开错误", "连接拒绝错误", "连接重置错误", "文件存在错误", "文件未找到错误", "中断错误",
            "是目录错误", "不是目录错误", "权限错误", "进程查找错误", "超时错误", "引用错误", "运行时错误", "未实现错误",
            "递归错误", "语法错误", "缩进错误", "制表符错误", "系统错误", "类型错误", "值错误", "万国码错误",
            "编码错误", "解码错误", "翻译错误", "内存错误", "警告基类", "用户警告", "弃用警告", "未来警告",
            "挂起弃用警告", "语法警告", "运行时警告", "导入警告", "万国码警告", "字节警告", "资源警告"
        )

        private val OPERATORS = listOf(
            "**=", "//=", "**", "//", "==", "!=", "<=", ">=",
            "+=", "-=", "*=", "/=", "%=", ":=", "<<", ">>",
            "@", "+", "-", "*", "/", "%", "=", "<", ">",
            "&", "|", "^", "~", "."
        )

        private val PUNCTUATION = setOf('(', ')', '[', ']', '{', '}', ',', ';', ':')
    }
}
