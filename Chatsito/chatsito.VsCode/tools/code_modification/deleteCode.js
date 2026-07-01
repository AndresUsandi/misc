const vscode = require('vscode');
const path = require('path');

async function deleteCode(filePath, startLine, startChar, endLine, endChar) {
    if (!filePath) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const edit = new vscode.WorkspaceEdit();
        const range = new vscode.Range(new vscode.Position(startLine, startChar), new vscode.Position(endLine, endChar));
        edit.delete(uri, range);
        
        return {
            edit: edit,
            successMessage: `Successfully deleted code at ${vscode.workspace.asRelativePath(uri)} from line ${startLine + 1} to ${endLine + 1}`
        };
    } catch (e) {
        return `Error deleting code: ${e.message}`;
    }
}

module.exports = deleteCode;
