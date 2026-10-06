// PyCn VSCode 扩展：一键运行 .pycn 文件
const vscode = require('vscode');

function activate(context) {
    const disposable = vscode.commands.registerCommand('pycn.runFile', async (resource) => {
        let target = null;

        // 资源管理器右键：传入 Uri
        if (resource && resource.fsPath) {
            target = resource;
        } else {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                target = editor.document.uri;
            }
        }

        if (!target) {
            vscode.window.showWarningMessage('没有可运行的 PyCn 文件');
            return;
        }

        // 保存未保存的更改
        const docs = vscode.workspace.textDocuments.filter(
            (d) => d.uri.fsPath === target.fsPath
        );
        for (const doc of docs) {
            if (doc.isDirty) {
                await doc.save();
            }
        }

        const config = vscode.workspace.getConfiguration('pycn');
        const runner = config.get('runner', 'module');
        const python = config.get('pythonPath', 'python');
        const file = target.fsPath;

        let command;
        if (runner === 'pycn') {
            command = `pycn run "${file}"`;
        } else {
            command = `"${python}" -m pycn_lang run "${file}"`;
        }

        let terminal = vscode.window.activeTerminal;
        if (!terminal) {
            terminal = vscode.window.createTerminal('PyCn');
        }
        terminal.show(true);
        terminal.sendText(command);
    });

    context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = { activate, deactivate };
