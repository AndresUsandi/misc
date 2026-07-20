const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function listTests(projectPath) {
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

        const files = await vscode.workspace.findFiles(
            new vscode.RelativePattern(absPath, '**/*.{test,spec}.{js,ts,jsx,tsx}'),
            '**/node_modules/**|**/out/**|**/dist/**'
        );

        // Also include files ending in Tests.js or Test.js if any
        const files2 = await vscode.workspace.findFiles(
            new vscode.RelativePattern(absPath, '**/*Test{s,}.{js,ts}'),
            '**/node_modules/**|**/out/**|**/dist/**'
        );

        const allFiles = [...files, ...files2];
        const uniqueFiles = new Set(allFiles.map(f => f.fsPath));
        const tests = [];

        for (const fsPath of uniqueFiles) {
            const content = fs.readFileSync(fsPath, 'utf8');
            const lines = content.split('\n');
            let currentSuite = '';

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                const describeMatch = line.match(/describe\s*\(\s*['"]([^'"]+)['"]/);
                if (describeMatch) {
                    currentSuite = describeMatch[1];
                }

                const itMatch = line.match(/it\s*\(\s*['"]([^'"]+)['"]/);
                const testMatch = line.match(/test\s*\(\s*['"]([^'"]+)['"]/);
                
                if (itMatch || testMatch) {
                    const testName = itMatch ? itMatch[1] : testMatch[1];
                    tests.push({
                        file: vscode.workspace.asRelativePath(fsPath),
                        suite: currentSuite,
                        name: testName,
                        line: i + 1
                    });
                }
            }
        }

        if (tests.length === 0) {
            return `=== Test Discovery ===\n\nNo tests found in ${projectPath}.`;
        }

        let output = `=== Discovered Tests (${tests.length}) ===\n\n`;
        for (const t of tests) {
            output += `Suite: ${t.suite || 'Global'}\n`;
            output += `  Test:  ${t.name}\n`;
            output += `  File:  ${t.file}:${t.line}\n\n`;
        }

        return output;

    } catch (e) {
        return `Error listing tests: ${e.message}`;
    }
}

module.exports = listTests;
