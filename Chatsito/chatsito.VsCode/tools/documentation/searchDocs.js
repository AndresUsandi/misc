const vscode = require('vscode');
const fs = require('fs');

async function searchDocs(query) {
    if (!query) return "Error: Missing query parameter.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const absPath = workspaceFolders[0].uri.fsPath;
        const pattern = new vscode.RelativePattern(absPath, '**/*.md');
        const files = await vscode.workspace.findFiles(pattern, '**/node_modules/**');

        if (files.length === 0) {
            return `No markdown files found in workspace.`;
        }

        let output = `=== Documentation Search Results for "${query}" ===\n\n`;
        let matchCount = 0;

        for (const fileUri of files) {
            const content = fs.readFileSync(fileUri.fsPath, 'utf8');
            const lines = content.split('\n');
            let fileHasMatch = false;

            lines.forEach((line, index) => {
                if (line.includes(query)) {
                    if (!fileHasMatch) {
                        output += `File: ${vscode.workspace.asRelativePath(fileUri.fsPath)}\n`;
                        fileHasMatch = true;
                    }
                    output += `  Line ${index + 1}: ${line.trim()}\n`;
                    matchCount++;
                }
            });

            if (fileHasMatch) output += '\n';
        }

        if (matchCount === 0) {
            output += `No matches found for "${query}" in ${files.length} markdown files.`;
        } else {
            output += `Total matches: ${matchCount}`;
        }

        return output;

    } catch (e) {
        return `Error searching documentation: ${e.message}`;
    }
}

module.exports = searchDocs;
