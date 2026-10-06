package com.pycn.plugin

import com.intellij.lang.ASTNode
import com.intellij.lang.PsiBuilder
import com.intellij.lang.PsiParser
import com.intellij.psi.tree.IElementType

/**
 * 最小解析器：PyCn 的语义在运行时由 Python 负责，
 * IDE 侧只需构造完整 PSI 树以支持高亮、编辑与运行。
 */
class PycnParser : PsiParser {
    override fun parse(root: IElementType, builder: PsiBuilder): ASTNode {
        while (!builder.eof()) {
            builder.advanceLexer()
        }
        return builder.treeBuilt
    }
}
