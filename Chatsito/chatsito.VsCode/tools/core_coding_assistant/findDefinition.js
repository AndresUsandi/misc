const vscode = require('vscode');
const path = require('path');

async function findDefinition(filePath, line, character) {
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

        const position = new vscode.Position(line, character);
        // Ensure document is loaded
        await vscode.workspace.openTextDocument(uri);
        
        const definitions = await vscode.commands.executeCommand('vscode.executeDefinitionProvider', uri, position) || [];
        
        if (!definitions || (Array.isArray(definitions) && definitions.length === 0)) {
            return `No definitions found for symbol at ${vscode.workspace.asRelativePath(uri)}:${line + 1}:${character + 1}`;
        }

        let output = `=== Definition(s) Found ===\n\n`;
        const list = Array.isArray(definitions) ? definitions : [definitions];
        for (const def of list) {
            const targetUri = def.uri || def.targetUri;
            const targetRange = def.range || def.targetRange;
            if (targetUri && targetRange) {
                const relPath = vscode.workspace.asRelativePath(targetUri);
                output += `File: ${relPath}\nLine: ${targetRange.start.line + 1}\nCharacter: ${targetRange.start.character + 1}\nRange: Lines ${targetRange.start.line + 1} to ${targetRange.end.line + 1}\n\n`;
            }
        }

        return output;
    } catch (error) {
        return `Error finding definition: ${error.message}`;
    }
}

module.exports = findDefinition;
