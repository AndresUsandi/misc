const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

async function readDoc(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        let targetPath = filePath;

        if (!path.isAbsolute(targetPath)) {
            // Try resolving exactly as specified first
            let testPath = path.resolve(rootPath, filePath);
            if (!fs.existsSync(testPath) && !filePath.toLowerCase().endsWith('.md')) {
                testPath += '.md'; // try appending .md
            }

            if (!fs.existsSync(testPath)) {
                // Try resolving inside docs/ folder
                let docsPath = path.resolve(rootPath, 'docs', filePath);
                if (!fs.existsSync(docsPath) && !filePath.toLowerCase().endsWith('.md')) {
                    docsPath += '.md';
                }
                if (fs.existsSync(docsPath)) {
                    testPath = docsPath;
                }
            }
            targetPath = testPath;
        }

        if (!fs.existsSync(targetPath)) {
            return `Error: Documentation file not found: ${filePath}`;
        }

        const content = fs.readFileSync(targetPath, 'utf8');
        return `=== Documentation: ${vscode.workspace.asRelativePath(targetPath)} ===\n\n${content}`;

    } catch (e) {
        return `Error reading documentation: ${e.message}`;
    }
}

module.exports = readDoc;
