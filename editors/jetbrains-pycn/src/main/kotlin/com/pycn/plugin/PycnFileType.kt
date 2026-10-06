package com.pycn.plugin

import com.intellij.openapi.fileTypes.LanguageFileType
import com.intellij.icons.AllIcons
import javax.swing.Icon

object PycnFileType : LanguageFileType(PycnLanguage) {
    override fun getName(): String = "PyCn"

    override fun getDescription(): String = "PyCn 中文 Python 源文件"

    override fun getDefaultExtension(): String = "pycn"

    override fun getIcon(): Icon = AllIcons.FileTypes.Text

    @JvmStatic
    val INSTANCE: PycnFileType get() = this
}
