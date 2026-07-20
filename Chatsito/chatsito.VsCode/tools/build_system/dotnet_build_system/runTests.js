const { exec } = require('child_process');
const vscode = require('vscode');

async function runTests() {
    const wf = vscode.workspace.workspaceFolders;
    if (!wf) return "Error: No workspace open.";

    return new Promise(resolve => {
        exec('dotnet test --logger "console;verbosity=detailed"', { cwd: wf[0].uri.fsPath }, (err, stdout, stderr) => {
            let output = "=== Run Tests ===\n\n";
            output += stdout || "";
            if (stderr) output += "\nErrors:\n" + stderr;
            if (err && !stdout && !stderr) output += "\nFailed to execute: " + err.message;
            resolve(output.trim());
        });
    });
}

module.exports = runTests;
