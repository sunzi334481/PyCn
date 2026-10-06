package com.pycn.plugin

import com.intellij.openapi.fileChooser.FileChooserDescriptor
import com.intellij.openapi.options.SettingsEditor
import com.intellij.openapi.ui.TextFieldWithBrowseButton
import com.intellij.ui.components.JBLabel
import com.intellij.util.ui.FormBuilder
import javax.swing.JCheckBox
import javax.swing.JComponent
import javax.swing.JPanel
import javax.swing.JTextField

class PycnRunConfigurationEditor : SettingsEditor<PycnRunConfiguration>() {

    private val scriptField = TextFieldWithBrowseButton()
    private val pythonField = JTextField("python")
    private val argumentsField = JTextField()
    private val useCliCheckBox = JCheckBox("使用 pycn 命令（需要 pycn 在 PATH 中）")

    private val panel: JPanel

    init {
        scriptField.addBrowseFolderListener(
            "选择 PyCn 文件",
            "选择要运行的 .pycn 脚本",
            null,
            FileChooserDescriptor(true, false, false, false, false, false)
        )

        panel = FormBuilder.createFormBuilder()
            .addLabeledComponent(JBLabel("脚本："), scriptField)
            .addLabeledComponent(JBLabel("Python："), pythonField)
            .addLabeledComponent(JBLabel("脚本参数："), argumentsField)
            .addComponent(useCliCheckBox)
            .addComponentFillVertically(JPanel(), 0)
            .panel
    }

    override fun resetEditorFrom(config: PycnRunConfiguration) {
        scriptField.text = config.scriptPath
        pythonField.text = config.pythonCommand
        argumentsField.text = config.scriptArguments
        useCliCheckBox.isSelected = config.usePycnCli
    }

    override fun applyEditorTo(config: PycnRunConfiguration) {
        config.scriptPath = scriptField.text
        config.pythonCommand = pythonField.text
        config.scriptArguments = argumentsField.text
        config.usePycnCli = useCliCheckBox.isSelected
    }

    override fun createEditor(): JComponent = panel
}
