package com.pycn.plugin

import com.intellij.ide.highlighter.DefaultLanguageHighlighterColors
import com.intellij.openapi.fileTypes.SyntaxHighlighter
import com.intellij.openapi.options.colors.AttributesDescriptor
import com.intellij.openapi.options.colors.ColorDescriptor
import com.intellij.openapi.options.colors.ColorSettingsPage
import javax.swing.Icon

class PycnColorSettingsPage : ColorSettingsPage {

    private val descriptors = arrayOf(
        AttributesDescriptor("PyCn//关键字", DefaultLanguageHighlighterColors.KEYWORD),
        AttributesDescriptor("PyCn//内置函数", DefaultLanguageHighlighterColors.FUNCTION_CALL),
        AttributesDescriptor("PyCn//异常", DefaultLanguageHighlighterColors.CLASS_NAME),
        AttributesDescriptor("PyCn//字符串", DefaultLanguageHighlighterColors.STRING),
        AttributesDescriptor("PyCn//数字", DefaultLanguageHighlighterColors.NUMBER),
        AttributesDescriptor("PyCn//注释", DefaultLanguageHighlighterColors.LINE_COMMENT),
        AttributesDescriptor("PyCn//运算符", DefaultLanguageHighlighterColors.OPERATION_SIGN)
    )

    override fun getDisplayName(): String = "PyCn"

    override fun getIcon(): Icon? = null

    override fun getAttributeDescriptors(): Array<AttributesDescriptor> = descriptors

    override fun getColorDescriptors(): Array<ColorDescriptor> = ColorDescriptor.EMPTY_ARRAY

    override fun getHighlighter(): SyntaxHighlighter = PycnSyntaxHighlighter()

    override fun getDemoText(): String = """
        # 计算阶乘
        定义 阶乘(数):
            如果 数 <= 1:
                返回 1
            返回 数 * 阶乘(数 - 1)

        尝试:
            打印(格"结果：{阶乘(5)}")
        捕获 值错误 作为 e:
            打印(e)
    """.trimIndent()

    override fun getAdditionalHighlightingTagToDescriptorMap(): Map<String, com.intellij.openapi.editor.colors.TextAttributesKey>? = null
}
