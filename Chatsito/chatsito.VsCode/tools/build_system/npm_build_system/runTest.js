const { exec } = require('child_process');
const path = require('path');
const vscode = require('vscode');

async function runTest(projectPath, testName) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    if (!testName) return "Error: Missing testName parameter.";

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

        // We assume mocha/jest style where -g or -t runs specific tests. For npm test, we pass arguments.
        // E.g. npm test -- -g "testName"
        let command = `npm test -- -g "${testName.replace(/"/g, '\\"')}"`;

        return new Promise((resolve) => {
            exec(command, { cwd: absPath, maxBuffer: 1024 * 1024 * 10 }, (error, stdout, stderr) => {
                let output = `=== Specific Test Results ===\n\n`;
                if (stdout) output += `STDOUT:\n${stdout}\n`;
                if (stderr) output += `STDERR:\n${stderr}\n`;
                if (error) {
                    output += `\nError: Test '${testName}' failed with code ${error.code}\n${error.message}`;
                } else {
                    output += `\nTest '${testName}' passed successfully.`;
                }
                resolve(output);
            });
        });

    } catch (e) {
        return `Error running specific test: ${e.message}`;
    }
}

module.exports = runTest;
