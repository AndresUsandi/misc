const { exec } = require('child_process');
const path = require('path');
const vscode = require('vscode');

async function runTests(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    try {
        let absPath;
        if (path.isAbsolute(projectPath)) {
            absPath = projectPath;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, projectPath);
            } else {
                return `Error: Could not resolve relative path '${projectPath}'.`;
            }
        }

        let command = 'npm test'; // Default

        return new Promise((resolve) => {
            exec(command, { cwd: absPath, maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
                let output = `=== Test Results ===\n\n`;
                if (stdout) output += `STDOUT:\n${stdout}\n`;
                if (stderr) output += `STDERR:\n${stderr}\n`;
                if (error) {
                    output += `\nError: Tests failed with code ${error.code}\n${error.message}`;
                } else {
                    output += `\nAll tests passed successfully.`;
                }
                resolve(output);
            });
        });

    } catch (e) {
        return `Error running tests: ${e.message}`;
    }
}

module.exports = runTests;
