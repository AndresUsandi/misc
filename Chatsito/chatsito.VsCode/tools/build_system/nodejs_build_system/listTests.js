const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const { resolvePath } = require('./nodeHelper');

function findFilesSync(dir, fileRegex, ignoreDirs = ['node_modules', 'out', 'build', 'CMakeFiles', 'bin', '.git']) {
    let results = [];
    let list;
    try {
        list = fs.readdirSync(dir);
    } catch (e) {
        return [];
    }
    
    list.forEach(file => {
        const filePath = path.join(dir, file);
        try {
            const stat = fs.statSync(filePath);
            if (stat && stat.isDirectory()) {
                if (!ignoreDirs.includes(file)) {
                    results = results.concat(findFilesSync(filePath, fileRegex, ignoreDirs));
                }
            } else {
                if (fileRegex.test(file)) {
                    results.push(filePath);
                }
            }
        } catch (e) {}
    });
    return results;
}

async function listTests(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    try {
        const absPath = resolvePath(projectPath);

        // Find Node.js test files: *.test.js/ts, *.spec.js/ts, or CamelCase like *Tests.js
        const fileRegex = /.*[._-]?test(s)?\.(js|ts|jsx|tsx)$/i;
        const files = findFilesSync(absPath, fileRegex);

        const tests = [];

        for (const fsPath of files) {
            const content = fs.readFileSync(fsPath, 'utf8');
            const lines = content.split('\n');
            let currentSuite = '';

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];

                // Detect describe block suites
                const suiteMatch = line.match(/\bdescribe\s*\(\s*["']([^"']+)["']/);
                if (suiteMatch) {
                    currentSuite = suiteMatch[1];
                }

                // Detect test or it cases
                const testMatch = line.match(/\b(?:test|it)\s*\(\s*["']([^"']+)["']/);
                if (testMatch) {
                    const testName = testMatch[1];
                    tests.push({
                        file: vscode.workspace.asRelativePath(fsPath).replace(/\\/g, '/'),
                        suite: currentSuite || 'Default Suite',
                        name: testName,
                        line: i + 1
                    });
                }
            }
        }

        if (tests.length === 0) {
            return `=== Node.js Test Discovery ===\n\nNo Node.js tests found in ${projectPath}.`;
        }

        let output = `=== Discovered Tests (${tests.length}) ===\n\n`;
        for (const t of tests) {
            output += `Suite: ${t.suite}\n`;
            output += `  Test:  ${t.name}\n`;
            output += `  File:  ${t.file}:${t.line}\n\n`;
        }

        return output;

    } catch (e) {
        return `Error listing Node.js tests: ${e.message}`;
    }
}

module.exports = listTests;
