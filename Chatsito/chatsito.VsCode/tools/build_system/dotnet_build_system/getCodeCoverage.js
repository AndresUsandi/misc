const { exec } = require('child_process');
const vscode = require('vscode');

async function getCodeCoverage() {
    const wf = vscode.workspace.workspaceFolders;
    if (!wf) return "Error: No workspace open.";

    return new Promise(resolve => {
        exec('dotnet test --collect:"XPlat Code Coverage"', { cwd: wf[0].uri.fsPath }, (err, stdout, stderr) => {
            let output = "=== Code Coverage Collection ===\n\n";
            output += stdout || "";
            if (stderr) output += "\nErrors:\n" + stderr;
            if (err && !stdout && !stderr) output += "\nFailed to execute: " + err.message;
            output += "\n\nNote: If coverage files were generated, look in the TestResults directory for coverage.cobertura.xml.";
            resolve(output.trim());
        });
    });
}

module.exports = getCodeCoverage;
