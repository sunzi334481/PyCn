package com.pycn.plugin

import com.intellij.lang.Language

object PycnLanguage : Language("pycn") {
    override fun getDisplayName(): String = "PyCn"

    override fun isCaseSensitive(): Boolean = true

    @JvmStatic
    val INSTANCE: PycnLanguage get() = this
}
