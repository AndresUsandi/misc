const vscode = require('vscode');
const path = require('path');
const { validateRequiredParams } = require('./codeUtils');

async function moveFile(args) {
    let sourcePath, destPath;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ sourcePath, destPath } = args);
    } else {
        sourcePath = arguments[0];
        destPath = arguments[1];
    }

    const normalizedArgs = { sourcePath, destPath };
    const validationErr = validateRequiredParams("moveFile", normalizedArgs);
    if (validationErr) {
        return validationErr;
    }

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
