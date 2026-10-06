package com.pycn.plugin

import com.intellij.ide.highlighter.DefaultLanguageHighlighterColors
import com.intellij.openapi.editor.colors.TextAttributesKey
import com.intellij.openapi.fileTypes.SyntaxHighlighter
import com.intellij.openapi.fileTypes.SyntaxHighlighterBase
import com.intellij.openapi.fileTypes.SyntaxHighlighterFactory
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.psi.tree.IElementType

class PycnSyntaxHighlighter : SyntaxHighlighterBase() {

    override fun getHighlightingLexer() = PycnLexer()

    override fun getTokenHighlights(tokenType: IElementType?): Array<TextAttributesKey> =
        when (tokenType) {
            PycnTokenTypes.注释 -> arrayOf(DefaultLanguageHighlighterColors.LINE_COMMENT)
            PycnTokenTypes.字符串 -> arrayOf(DefaultLanguageHighlighterColors.STRING)
            PycnTokenTypes.数字 -> arrayOf(DefaultLanguageHighlighterColors.NUMBER)
            PycnTokenTypes.关键字 -> arrayOf(DefaultLanguageHighlighterColors.KEYWORD)
            PycnTokenTypes.内置函数 -> arrayOf(DefaultLanguageHighlighterColors.FUNCTION_CALL)
            PycnTokenTypes.异常名 -> arrayOf(DefaultLanguageHighlighterColors.CLASS_NAME)
            PycnTokenTypes.运算符 -> arrayOf(DefaultLanguageHighlighterColors.OPERATION_SIGN)
            PycnTokenTypes.标点 -> arrayOf(DefaultLanguageHighlighterColors.PARENTHESES)
            else -> emptyArray()
        }
}

class PycnSyntaxHighlighterFactory : SyntaxHighlighterFactory() {
    override fun getSyntaxHighlighter(project: Project?, virtualFile: VirtualFile?): SyntaxHighlighter =
        PycnSyntaxHighlighter()
}
