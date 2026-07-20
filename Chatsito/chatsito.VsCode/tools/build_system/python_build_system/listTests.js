const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const { resolvePath } = require('./pythonHelper');

function findFilesSync(dir, fileRegex, ignoreDirs = ['node_modules', 'out', 'build', 'CMakeFiles', 'bin', '.git', '.venv', 'venv', 'env']) {
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

        // Find Python test files: test_*.py or *_test.py
        const fileRegex = /^(test_.*|.*_test)\.py$/;
        const files = findFilesSync(absPath, fileRegex);

        const tests = [];

        for (const fsPath of files) {
            const content = fs.readFileSync(fsPath, 'utf8');
            const lines = content.split('\n');
            let currentClass = '';

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];

                // Detect classes: class TestSomething
                const classMatch = line.match(/^\s*class\s+([a-zA-Z0-9_]+)/);
                if (classMatch) {
                    currentClass = classMatch[1];
                }

                // Detect test functions: def test_something
                const funcMatch = line.match(/^\s*def\s+(test_[a-zA-Z0-9_]+)\s*\(/);
                if (funcMatch) {
                    const testName = funcMatch[1];
                    tests.push({
                        file: vscode.workspace.asRelativePath(fsPath).replace(/\\/g, '/'),
                        className: currentClass || 'Module level',
                        name: testName,
                        line: i + 1
                    });
                }
            }
        }

        if (tests.length === 0) {
            return `=== Python Test Discovery ===\n\nNo Python tests found in ${projectPath}.`;
        }

        let output = `=== Discovered Python Tests (${tests.length}) ===\n\n`;
        for (const t of tests) {
            output += `Class/Module: ${t.className}\n`;
            output += `  Test:  ${t.name}\n`;
            output += `  File:  ${t.file}:${t.line}\n\n`;
        }

        return output;

    } catch (e) {
        return `Error listing Python tests: ${e.message}`;
    }
}

module.exports = listTests;
