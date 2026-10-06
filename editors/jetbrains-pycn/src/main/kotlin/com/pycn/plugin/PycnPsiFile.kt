package com.pycn.plugin

import com.intellij.extapi.psi.PsiFileBase
import com.intellij.openapi.fileTypes.FileType
import com.intellij.psi.FileViewProvider

class PycnPsiFile(viewProvider: FileViewProvider) : PsiFileBase(viewProvider, PycnLanguage) {
    override fun getFileType(): FileType = PycnFileType

    override fun toString(): String = "PyCn 文件"
}
