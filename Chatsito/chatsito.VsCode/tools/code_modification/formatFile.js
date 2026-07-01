const vscode = require('vscode');
const path = require('path');

async function formatFile(filePath) {
    if (!filePath) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const doc = await vscode.workspace.openTextDocument(uri);
        // Execute format document provider
        const edits = await vscode.commands.executeCommand('vscode.executeFormatDocumentProvider', uri, {
            insertSpaces: true,
            tabSize: 4
        });
        
        if (edits && edits.length > 0) {
            const edit = new vscode.WorkspaceEdit();
            for (const e of edits) {
                edit.replace(uri, e.range, e.newText);
            }
            return {
                edit: edit,
                successMessage: `Successfully formatted file ${vscode.workspace.asRelativePath(uri)}.`
            };
        } else {
            return `No formatting changes required or no formatter available for this file.`;
        }
    } catch (e) {
        return `Error formatting file: ${e.message}`;
    }
}

module.exports = formatFile;
