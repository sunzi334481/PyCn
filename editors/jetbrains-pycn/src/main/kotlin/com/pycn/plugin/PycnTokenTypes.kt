package com.pycn.plugin

import com.intellij.psi.tree.IElementType

class PycnTokenType(debugName: String) : IElementType(debugName, PycnLanguage)

object PycnTokenTypes {
    val 空白 = PycnTokenType("空白")
    val 注释 = PycnTokenType("注释")
    val 字符串 = PycnTokenType("字符串")
    val 数字 = PycnTokenType("数字")
    val 关键字 = PycnTokenType("关键字")
    val 内置函数 = PycnTokenType("内置函数")
    val 异常名 = PycnTokenType("异常")
    val 名字 = PycnTokenType("名字")
    val 运算符 = PycnTokenType("运算符")
    val 标点 = PycnTokenType("标点")
}
