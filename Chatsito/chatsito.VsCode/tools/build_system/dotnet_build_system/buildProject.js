const { exec } = require('child_process');
const vscode = require('vscode');

async function buildProject(projectPath) {
    if (!projectPath) return "Error: No project path provided.";
    const wf = vscode.workspace.workspaceFolders;
    if (!wf) return "Error: No workspace open.";

    return new Promise(resolve => {
        exec(`dotnet build "${projectPath}"`, { cwd: wf[0].uri.fsPath }, (err, stdout, stderr) => {
            let output = `=== Build Project: ${projectPath} ===\n\n`;
            output += stdout || "";
            if (stderr) output += "\nErrors:\n" + stderr;
            if (err && !stdout && !stderr) output += "\nFailed to execute: " + err.message;
            resolve(output.trim());
        });
    });
}

module.exports = buildProject;
