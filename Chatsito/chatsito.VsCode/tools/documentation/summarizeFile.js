const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

async function summarizeFile(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        let absPath = filePath;
        
        if (!path.isAbsolute(filePath)) {
            absPath = path.resolve(rootPath, filePath);
        }

        if (!fs.existsSync(absPath)) {
            return `Error: File not found: ${filePath}`;
        }

        const content = fs.readFileSync(absPath, 'utf8');
        const lines = content.split('\n');
        
        let importsCount = 0;
        let classesCount = 0;
        let functionsCount = 0;

        lines.forEach(line => {
            const trimmed = line.trim();
            // Basic heuristics
            if (trimmed.startsWith('import ') || trimmed.includes('require(')) {
                importsCount++;
            }
            if (trimmed.startsWith('class ') || trimmed.includes(' class ')) {
                classesCount++;
            }
            if (trimmed.startsWith('function ') || trimmed.includes(' function ') || trimmed.includes('=>') || trimmed.includes('public ') || trimmed.includes('private ')) {
                // simple heuristic for functions/methods
                if (trimmed.includes('(') && trimmed.includes(')')) {
                    functionsCount++;
                }
            }
        });

        let output = `=== Summary for ${vscode.workspace.asRelativePath(absPath)} ===\n\n`;
        output += `Total Lines: ${lines.length}\n`;
        output += `File Size: ${(fs.statSync(absPath).size / 1024).toFixed(2)} KB\n\n`;
        output += `Detected Elements (heuristic-based):\n`;
        output += `- Imports/Requires: ${importsCount}\n`;
        output += `- Classes: ${classesCount}\n`;
        output += `- Functions/Methods: ${functionsCount}\n`;

        return output;

    } catch (e) {
        return `Error summarizing file: ${e.message}`;
    }
}

module.exports = summarizeFile;
