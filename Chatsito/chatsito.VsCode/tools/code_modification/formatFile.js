const vscode = require('vscode');
const path = require('path');
const { validateRequiredParams } = require('./codeUtils');

async function formatFile(args) {
    let filePath;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ filePath } = args);
    } else {
        filePath = arguments[0];
    }

    const normalizedArgs = { filePath };
    const validationErr = validateRequiredParams("formatFile", normalizedArgs);
    if (validationErr) {
        return validationErr;
    }

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const doc = await vscode.workspace.openTextDocument(uri);
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
