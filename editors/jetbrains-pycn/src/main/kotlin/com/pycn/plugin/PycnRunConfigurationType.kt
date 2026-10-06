package com.pycn.plugin

import com.intellij.execution.configurations.ConfigurationFactory
import com.intellij.execution.configurations.ConfigurationType
import com.intellij.execution.configurations.RunConfiguration
import com.intellij.icons.AllIcons
import com.intellij.openapi.project.Project
import javax.swing.Icon

class PycnRunConfigurationType : ConfigurationType {

    override fun getDisplayName(): String = "PyCn"

    override fun getConfigurationTypeDescription(): String = "运行 PyCn (.pycn) 程序"

    override fun getIcon(): Icon = AllIcons.RunConfigurations.Application

    override fun getId(): String = ID

    override fun getConfigurationFactories(): Array<ConfigurationFactory> =
        arrayOf(PycnRunConfigurationFactory(this))

    companion object {
        const val ID = "PycnRunConfiguration"
    }
}

class PycnRunConfigurationFactory(type: ConfigurationType) : ConfigurationFactory(type) {

    override fun getId(): String = "PyCn"

    override fun createTemplateConfiguration(project: Project): RunConfiguration =
        PycnRunConfiguration(project, this, "PyCn")
}
