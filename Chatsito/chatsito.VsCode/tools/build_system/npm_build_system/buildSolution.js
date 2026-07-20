const { exec } = require('child_process');
const path = require('path');
const vscode = require('vscode');

async function buildSolution(solutionPath) {
    if (!solutionPath) return "Error: Missing solutionPath parameter.";

    try {
        let absPath;
        if (path.isAbsolute(solutionPath)) {
            absPath = solutionPath;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, solutionPath);
            } else {
                return `Error: Could not resolve relative path '${solutionPath}'.`;
            }
        }

        let command = 'npm run build'; // Default

        return new Promise((resolve) => {
            exec(command, { cwd: absPath, maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
                let output = `=== Solution Build Results ===\n\n`;
                if (stdout) output += `STDOUT:\n${stdout}\n`;
                if (stderr) output += `STDERR:\n${stderr}\n`;
                if (error) {
                    output += `\nError: Build failed with code ${error.code}\n${error.message}`;
                } else {
                    output += `\nSolution build succeeded.`;
                }
                resolve(output);
            });
        });

    } catch (e) {
        return `Error building solution: ${e.message}`;
    }
}

module.exports = buildSolution;
