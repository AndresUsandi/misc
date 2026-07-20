const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const { resolvePath } = require('./cHelper');

function findFilesSync(dir, fileRegex, ignoreDirs = ['node_modules', 'out', 'build', 'CMakeFiles', 'bin']) {
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

        // Find C/C++ source files synchronously
        const fileRegex = /.*\.(c|cpp|cc|cxx)$/;
        const files = findFilesSync(absPath, fileRegex);

        const tests = [];

        for (const fsPath of files) {
            const content = fs.readFileSync(fsPath, 'utf8');
            const lines = content.split('\n');

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];

                // Google Test: TEST(Suite, Name) or TEST_F(Suite, Name)
                const gtestMatch = line.match(/\bTEST(?:_F)?\s*\(\s*([a-zA-Z0-9_]+)\s*,\s*([a-zA-Z0-9_]+)\s*\)/);
                if (gtestMatch) {
                    tests.push({
                        framework: 'Google Test',
                        file: vscode.workspace.asRelativePath(fsPath),
                        suite: gtestMatch[1],
                        name: gtestMatch[2],
                        line: i + 1
                    });
                }

                // Catch2: TEST_CASE("Name", "[tags]")
                const catchMatch = line.match(/\bTEST_CASE\s*\(\s*["']([^"']+)["']/);
                if (catchMatch) {
                    tests.push({
                        framework: 'Catch2',
                        file: vscode.workspace.asRelativePath(fsPath),
                        suite: 'Catch2 Test Cases',
                        name: catchMatch[1],
                        line: i + 1
                    });
                }
            }
        }

        if (tests.length === 0) {
            return `=== C/C++ Test Discovery ===\n\nNo Google Test or Catch2 tests found in ${projectPath}.`;
        }

        let output = `=== Discovered C/C++ Tests (${tests.length}) ===\n\n`;
        for (const t of tests) {
            output += `Framework: ${t.framework}\n`;
            output += `  Suite: ${t.suite}\n`;
            output += `  Test:  ${t.name}\n`;
            output += `  File:  ${t.file}:${t.line}\n\n`;
        }

        return output;

    } catch (e) {
        return `Error listing C/C++ tests: ${e.message}`;
    }
}

module.exports = listTests;
