const { exec } = require('child_process');
const vscode = require('vscode');

async function listTests() {
    const wf = vscode.workspace.workspaceFolders;
    if (!wf) return "Error: No workspace open.";

    return new Promise(resolve => {
        exec('dotnet test --list-tests', { cwd: wf[0].uri.fsPath }, (err, stdout, stderr) => {
            let output = "=== Available Tests ===\n\n";
            output += stdout || "";
            if (stderr) output += "\nErrors:\n" + stderr;
            if (err && !stdout && !stderr) output += "\nFailed to execute: " + err.message;
            resolve(output.trim());
        });
    });
}

module.exports = listTests;
