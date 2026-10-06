package com.pycn.plugin

import com.intellij.execution.Executor
import com.intellij.execution.configurations.GeneralCommandLine
import com.intellij.execution.configurations.LocatableConfigurationBase
import com.intellij.execution.configurations.RunConfiguration
import com.intellij.execution.configurations.RunProfileState
import com.intellij.execution.process.ColoredProcessHandler
import com.intellij.execution.runners.ExecutionEnvironment
import com.intellij.execution.ui.ConsoleView
import com.intellij.execution.DefaultExecutionResult
import com.intellij.execution.ExecutionException
import com.intellij.util.execution.ParametersListUtil
import com.intellij.execution.ExecutionResult
import com.intellij.execution.configurations.CommandLineState
import com.intellij.openapi.options.SettingsEditor
import com.intellij.openapi.project.Project
import org.jdom.Element
import java.io.File

class PycnRunConfiguration(
    project: Project,
    factory: com.intellij.execution.configurations.ConfigurationFactory,
    name: String
) : LocatableConfigurationBase<RunProfileState>(project, factory, name) {

    var scriptPath: String = ""
    var pythonCommand: String = "python"
    var scriptArguments: String = ""
    var usePycnCli: Boolean = false

    override fun getConfigurationEditor(): SettingsEditor<out RunConfiguration> =
        PycnRunConfigurationEditor()

    override fun getState(executor: Executor, environment: ExecutionEnvironment): RunProfileState =
        PycnRunState(environment, this)

    override fun writeXML(element: Element) {
        super.writeXML(element)
        element.setAttribute("script", scriptPath)
        element.setAttribute("python", pythonCommand)
        element.setAttribute("args", scriptArguments)
        element.setAttribute("useCli", usePycnCli.toString())
    }

    override fun readXML(element: Element) {
        super.readXML(element)
        scriptPath = element.getAttributeValue("script") ?: ""
        pythonCommand = element.getAttributeValue("python") ?: "python"
        scriptArguments = element.getAttributeValue("args") ?: ""
        usePycnCli = element.getAttributeValue("useCli")?.toBoolean() ?: false
    }
}

class PycnRunState(
    environment: ExecutionEnvironment,
    private val config: PycnRunConfiguration
) : CommandLineState(environment) {

    @Throws(ExecutionException::class)
    override fun startProcess(): com.intellij.execution.process.ProcessHandler {
        if (config.scriptPath.isBlank()) {
            throw ExecutionException("请先在运行配置中指定 .pycn 脚本路径")
        }

        val commandLine = GeneralCommandLine()
        if (config.usePycnCli) {
            commandLine.exePath = "pycn"
            commandLine.addParameters("run", config.scriptPath)
        } else {
            commandLine.exePath = config.pythonCommand
            commandLine.addParameters("-m", "pycn_lang", "run", config.scriptPath)
        }
        if (config.scriptArguments.isNotBlank()) {
            // 用标准解析器替代 split(' ')，支持带空格的引号参数
            commandLine.addParameters(*ParametersListUtil.parse(config.scriptArguments).toTypedArray())
        }
        commandLine.workDirectory = File(config.project.basePath ?: ".")
        return ColoredProcessHandler(commandLine)
    }
}
