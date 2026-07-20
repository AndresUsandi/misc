const { exec } = require('child_process');
const vscode = require('vscode');

async function buildSolution() {
    const wf = vscode.workspace.workspaceFolders;
    if (!wf) return "Error: No workspace open.";

    return new Promise(resolve => {
        exec('dotnet build', { cwd: wf[0].uri.fsPath }, (err, stdout, stderr) => {
            let output = "=== Build Solution ===\n\n";
            output += stdout || "";
            if (stderr) output += "\nErrors:\n" + stderr;
            if (err && !stdout && !stderr) output += "\nFailed to execute: " + err.message;
            resolve(output.trim());
        });
    });
}

module.exports = buildSolution;
