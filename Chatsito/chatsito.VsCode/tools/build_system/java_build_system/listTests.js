const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const { resolvePath } = require('./javaHelper');

function findFilesSync(dir, fileRegex, ignoreDirs = ['node_modules', 'out', 'target', 'build', 'bin']) {
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

        // Find java test files synchronously
        const fileRegex = /.*Test(s)?\.java$/;
        const files = findFilesSync(absPath, fileRegex);

        const tests = [];

        for (const fsPath of files) {
            const content = fs.readFileSync(fsPath, 'utf8');
            const lines = content.split('\n');
            let currentClass = '';

            // Extract package name
            let packageName = '';
            for (const line of lines) {
                const pkgMatch = line.match(/^\s*package\s+([a-zA-Z0-9_.]+)\s*;/);
                if (pkgMatch) {
                    packageName = pkgMatch[1];
                    break;
                }
            }

            for (let i = 0; i < lines.length; i++) {
                const line = lines[i];
                
                const classMatch = line.match(/(?:public\s+)?class\s+([a-zA-Z0-9_]+)/);
                if (classMatch) {
                    currentClass = packageName ? `${packageName}.${classMatch[1]}` : classMatch[1];
                }

                const hasTestAnnotation = line.match(/@(?:org\.junit\.)?(?:jupiter\.api\.)?Test\b/);
                if (hasTestAnnotation) {
                    for (let j = i + 1; j < Math.min(lines.length, i + 5); j++) {
                        const methodMatch = lines[j].match(/(?:public|private|protected|void|\s)+\s+([a-zA-Z0-9_]+)\s*\(\s*\)/);
                        if (methodMatch) {
                            const methodName = methodMatch[1];
                            tests.push({
                                file: vscode.workspace.asRelativePath(fsPath),
                                className: currentClass,
                                name: methodName,
                                line: j + 1
                            });
                            break;
                        }
                    }
                }
            }
        }

        if (tests.length === 0) {
            return `=== Java Test Discovery ===\n\nNo Java JUnit tests found in ${projectPath}.`;
        }

        let output = `=== Discovered Java JUnit Tests (${tests.length}) ===\n\n`;
        for (const t of tests) {
            output += `Class: ${t.className || 'Unknown'}\n`;
            output += `  Test:  ${t.name}\n`;
            output += `  File:  ${t.file}:${t.line}\n\n`;
        }

        return output;

    } catch (e) {
        return `Error listing Java tests: ${e.message}`;
    }
}

module.exports = listTests;
