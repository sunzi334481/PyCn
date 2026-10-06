package com.pycn.plugin

import com.intellij.extapi.psi.ASTWrapperPsiElement
import com.intellij.lang.ASTNode
import com.intellij.lang.ParserDefinition
import com.intellij.lang.PsiParser
import com.intellij.lexer.Lexer
import com.intellij.openapi.project.Project
import com.intellij.psi.FileViewProvider
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiFile
import com.intellij.psi.tree.IFileElementType
import com.intellij.psi.tree.TokenSet

class PycnParserDefinition : ParserDefinition {

    companion object {
        val FILE = IFileElementType(PycnLanguage)
    }

    override fun createLexer(project: Project?): Lexer = PycnLexer()

    override fun createParser(project: Project?): PsiParser = PycnParser()

    override fun getFileNodeType(): IFileElementType = FILE

    override fun getWhitespaceTokens(): TokenSet = TokenSet.WHITE_SPACE

    override fun getCommentTokens(): TokenSet = TokenSet.create(PycnTokenTypes.注释)

    override fun getStringLiteralElements(): TokenSet = TokenSet.create(PycnTokenTypes.字符串)

    override fun createElement(node: ASTNode): PsiElement = ASTWrapperPsiElement(node)

    override fun createFile(viewProvider: FileViewProvider): PsiFile = PycnPsiFile(viewProvider)
}
