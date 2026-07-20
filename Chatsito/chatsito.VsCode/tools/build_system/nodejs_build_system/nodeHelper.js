const { exec } = require('child_process');
const path = require('path');
const vscode = require('vscode');

function resolvePath(targetPath) {
    if (!targetPath) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            return workspaceFolders[0].uri.fsPath;
        }
        return process.cwd();
    }
    if (path.isAbsolute(targetPath)) {
        return targetPath;
    }
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        return path.resolve(workspaceFolders[0].uri.fsPath, targetPath);
    }
    return path.resolve(targetPath);
}

function runNodeCommand(projectPath, command, header = "Node.js Command Results", successMessage = "Command executed successfully.") {
    const absPath = resolvePath(projectPath);
    return new Promise((resolve) => {
        exec(command, { cwd: absPath, maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
            let output = `=== ${header} ===\n\n`;
            if (stdout) output += `STDOUT:\n${stdout}\n`;
            if (stderr) output += `STDERR:\n${stderr}\n`;
            if (error) {
                output += `\nError: Command failed with code ${error.code}\n${error.message}`;
            } else {
                output += `\n${successMessage}`;
            }
            resolve(output);
        });
    });
}

module.exports = {
    resolvePath,
    runNodeCommand
};
