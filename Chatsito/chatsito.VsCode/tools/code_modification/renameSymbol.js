const vscode = require('vscode');
const path = require('path');

async function renameSymbol(filePath, line, character, newName) {
    if (!filePath || !newName) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const position = new vscode.Position(line, character);
        // Ensure doc is open
        await vscode.workspace.openTextDocument(uri);
        
        // Execute the rename provider
        const workspaceEdit = await vscode.commands.executeCommand('vscode.executeDocumentRenameProvider', uri, position, newName);
        
        if (workspaceEdit) {
            return {
                edit: workspaceEdit,
                successMessage: `Successfully renamed symbol to '${newName}'.`
            };
        } else {
            return `No rename provider found or rename not possible at this location.`;
        }
    } catch (e) {
        return `Error renaming symbol: ${e.message}`;
    }
}

module.exports = renameSymbol;
