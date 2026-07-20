const { exec } = require('child_process');
const vscode = require('vscode');

async function runTest(testName) {
    if (!testName) return "Error: No test name provided.";
    const wf = vscode.workspace.workspaceFolders;
    if (!wf) return "Error: No workspace open.";

    return new Promise(resolve => {
        exec(`dotnet test --filter FullyQualifiedName~${testName} --logger "console;verbosity=detailed"`, { cwd: wf[0].uri.fsPath }, (err, stdout, stderr) => {
            let output = `=== Run Test: ${testName} ===\n\n`;
            output += stdout || "";
            if (stderr) output += "\nErrors:\n" + stderr;
            if (err && !stdout && !stderr) output += "\nFailed to execute: " + err.message;
            resolve(output.trim());
        });
    });
}

module.exports = runTest;
