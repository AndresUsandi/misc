const vscode = require('vscode');
const path = require('path');

async function findReferences(filePath, line, character) {
    if (!filePath) return "Error: No file path provided.";

    try {
        let uri;
        if (path.isAbsolute(filePath)) {
            uri = vscode.Uri.file(filePath);
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                uri = vscode.Uri.file(path.resolve(workspaceFolders[0].uri.fsPath, filePath));
            } else {
                return `Error: Could not resolve relative path '${filePath}' because no workspace folders are open.`;
            }
        }

        let position = new vscode.Position(line, character);
        const doc = await vscode.workspace.openTextDocument(uri);
        
        let references = await vscode.commands.executeCommand('vscode.executeReferenceProvider', uri, position) || [];
        
        if (references.length === 0 && line + 1 < doc.lineCount) {
            const backupPosition = new vscode.Position(line + 1, character);
            const backupRefs = await vscode.commands.executeCommand('vscode.executeReferenceProvider', uri, backupPosition);
            if (backupRefs && backupRefs.length > 0) {
                references = backupRefs;
                position = backupPosition;
            }
        }
        
        if (references.length === 0) {
            return `No references found for symbol at ${vscode.workspace.asRelativePath(uri)}:${line + 1}:${character + 1}`;
        }

        let output = `=== References Found (${references.length} occurrences) ===\n\n`;
        for (const ref of references) {
            const refDoc = await vscode.workspace.openTextDocument(ref.uri);
            const lineText = refDoc.lineAt(ref.range.start.line).text.trim();
            const relPath = vscode.workspace.asRelativePath(ref.uri);
            output += `${relPath}:${ref.range.start.line + 1}:${ref.range.start.character + 1} -> ${lineText}\n`;
        }

        return output;
    } catch (error) {
        return `Error finding references: ${error.message}`;
    }
}

module.exports = findReferences;
