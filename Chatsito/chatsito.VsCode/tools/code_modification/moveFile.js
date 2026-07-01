const vscode = require('vscode');
const path = require('path');

async function moveFile(sourcePath, destPath) {
    if (!sourcePath || !destPath) return "Error: Missing required parameters.";

    try {
        let sourceUri, destUri;
        
        const PathResolver = require('../../PathResolver');

        try {
            sourceUri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(sourcePath));
            destUri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(destPath));
        } catch (err) {
            return `Error: ${err.message}`;
        }

        const edit = new vscode.WorkspaceEdit();
        edit.renameFile(sourceUri, destUri, { overwrite: false });
        
        return {
            edit: edit,
            successMessage: `Successfully moved/renamed file to ${vscode.workspace.asRelativePath(destUri)}`
        };
    } catch (e) {
        return `Error moving file: ${e.message}`;
    }
}

module.exports = moveFile;
