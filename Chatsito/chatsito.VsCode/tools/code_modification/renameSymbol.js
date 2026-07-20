const vscode = require('vscode');
const path = require('path');
const { validateRequiredParams } = require('./codeUtils');

async function renameSymbol(args) {
    let filePath, lineVal, charVal, newName;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ filePath, line: lineVal, character: charVal, newName } = args);
    } else {
        filePath = arguments[0];
        lineVal = arguments[1];
        charVal = arguments[2];
        newName = arguments[3];
    }

    const normalizedArgs = { filePath, line: lineVal, character: charVal, newName };
    const validationErr = validateRequiredParams("renameSymbol", normalizedArgs);
    if (validationErr) {
        return validationErr;
    }

    const line = parseInt(lineVal, 10);
    const character = parseInt(charVal, 10);

    if (isNaN(line) || isNaN(character)) {
        return "Error: Coordinates line and character must be valid integers.";
    }

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));
        const doc = await vscode.workspace.openTextDocument(uri);

        // Try 1-based coordinates first
        let targetLine = line - 1;
        let targetChar = character - 1;

        if (targetLine < 0 || targetChar < 0) {
            targetLine = line;
            targetChar = character;
        }

        let position = new vscode.Position(targetLine, targetChar);
        let workspaceEdit = await vscode.commands.executeCommand('vscode.executeDocumentRenameProvider', uri, position, newName);
        
        // Fallback 1: Try 0-based coordinates if different
        if (!workspaceEdit && (targetLine !== line || targetChar !== character)) {
            const pos0 = new vscode.Position(line, character);
            workspaceEdit = await vscode.commands.executeCommand('vscode.executeDocumentRenameProvider', uri, pos0, newName);
        }

        // Fallback 2: Backup line fallback
        if (!workspaceEdit && targetLine + 1 < doc.lineCount) {
            const posBackup = new vscode.Position(targetLine + 1, targetChar);
            workspaceEdit = await vscode.commands.executeCommand('vscode.executeDocumentRenameProvider', uri, posBackup, newName);
        }

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
