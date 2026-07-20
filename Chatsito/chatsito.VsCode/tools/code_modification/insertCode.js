const vscode = require('vscode');
const path = require('path');
const { validateRequiredParams } = require('./codeUtils');

async function insertCode(args) {
    let filePath, lineVal, charVal, textToInsert;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ filePath, line: lineVal, character: charVal, textToInsert } = args);
    } else {
        filePath = arguments[0];
        lineVal = arguments[1];
        charVal = arguments[2];
        textToInsert = arguments[3];
    }

    const normalizedArgs = { filePath, line: lineVal, character: charVal, textToInsert };
    const validationErr = validateRequiredParams("insertCode", normalizedArgs);
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

        const edit = new vscode.WorkspaceEdit();

        try {
            await vscode.workspace.fs.stat(uri);
        } catch {
            edit.createFile(uri);
        }

        let doc;
        try {
            doc = await vscode.workspace.openTextDocument(uri);
        } catch (e) {
            // Ignore error
        }

        // Try 1-based coordinate translation first
        let targetLine = line - 1;
        let targetChar = character - 1;

        if (targetLine < 0 || targetChar < 0) {
            // Fallback to 0-based coordinates
            targetLine = line;
            targetChar = character;
        }

        if (doc) {
            const maxLine = doc.lineCount - 1;
            targetLine = Math.min(Math.max(0, targetLine), maxLine);
            targetChar = Math.min(Math.max(0, targetChar), doc.lineAt(targetLine).text.length);
        } else {
            targetLine = Math.max(0, targetLine);
            targetChar = Math.max(0, targetChar);
        }

        let position = new vscode.Position(targetLine, targetChar);

        if (doc && targetChar > 0 && targetLine < doc.lineCount) {
            const linePrefix = doc.lineAt(targetLine).text.substring(0, targetChar);
            if (linePrefix.trim() === '' && /^\s/.test(textToInsert)) {
                edit.replace(uri, new vscode.Range(new vscode.Position(targetLine, 0), position), textToInsert);
                return {
                    edit: edit,
                    successMessage: `Successfully inserted code at ${vscode.workspace.asRelativePath(uri)}:${targetLine + 1}:${targetChar + 1}`
                };
            }
        }

        edit.insert(uri, position, textToInsert);

        return {
            edit: edit,
            successMessage: `Successfully inserted code at ${vscode.workspace.asRelativePath(uri)}:${targetLine + 1}:${targetChar + 1}`
        };
    } catch (e) {
        return `Error inserting code: ${e.message}`;
    }
}

module.exports = insertCode;
