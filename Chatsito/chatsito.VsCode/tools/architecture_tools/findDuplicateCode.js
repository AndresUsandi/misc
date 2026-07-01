const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function findDuplicateCode(directory) {
    if (!directory) return "Error: Missing directory parameter.";

    try {
        let absPath;
        if (path.isAbsolute(directory)) {
            absPath = directory;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, directory);
            } else {
                return `Error: Could not resolve relative path '${directory}' because no workspace folders are open.`;
            }
        }

        if (!fs.existsSync(absPath)) return `Error: Directory not found at '${absPath}'`;

        const files = await vscode.workspace.findFiles(
            new vscode.RelativePattern(absPath, '**/*.{js,ts,cs,java,py}'),
            '**/node_modules/**|**/bin/**|**/obj/**'
        );

        // Very naive line-based duplicate detection (chunk size 5)
        const CHUNK_SIZE = 5;
        const chunks = new Map();
        const duplicates = [];

        for (const uri of files) {
            const content = fs.readFileSync(uri.fsPath, 'utf8');
            const lines = content.split(/\r?\n/);
            
            for (let i = 0; i <= lines.length - CHUNK_SIZE; i++) {
                // Normalize lines: trim whitespace, ignore empty lines or single bracket lines
                let chunkText = "";
                let validLines = 0;
                for (let j = 0; j < CHUNK_SIZE; j++) {
                    const t = lines[i+j].trim();
                    if (t.length > 2) {
                        chunkText += t + "\n";
                        validLines++;
                    }
                }

                if (validLines >= Math.ceil(CHUNK_SIZE * 0.8)) {
                    // Hash or string match
                    if (chunks.has(chunkText)) {
                        const existing = chunks.get(chunkText);
                        // Prevent overlapping chunks in the same file from being flagged constantly
                        if (existing.file !== uri.fsPath || Math.abs(existing.line - i) > CHUNK_SIZE) {
                            duplicates.push({
                                file1: existing.file,
                                line1: existing.line,
                                file2: uri.fsPath,
                                line2: i,
                                code: chunkText
                            });
                        }
                    } else {
                        chunks.set(chunkText, { file: uri.fsPath, line: i });
                    }
                }
            }
        }

        if (duplicates.length === 0) {
            return `=== Duplicate Code Analysis ===\n\nNo significant duplicate code found.`;
        }

        let output = `=== Duplicate Code Found (${duplicates.length} instances) ===\n\n`;
        // Limit to 20 for output
        for (let k = 0; k < Math.min(duplicates.length, 20); k++) {
            const dup = duplicates[k];
            output += `Match ${k + 1}:\n`;
            output += `  Location 1: ${vscode.workspace.asRelativePath(dup.file1)}:${dup.line1 + 1}\n`;
            output += `  Location 2: ${vscode.workspace.asRelativePath(dup.file2)}:${dup.line2 + 1}\n`;
            output += `  Snippet:\n    ${dup.code.replace(/\n/g, '\n    ').trim()}\n\n`;
        }

        return output;
    } catch (e) {
        return `Error finding duplicate code: ${e.message}`;
    }
}

module.exports = findDuplicateCode;
