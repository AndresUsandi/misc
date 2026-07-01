const vscode = require('vscode');
const path = require('path');

async function insertCode(filePath, line, character, textToInsert) {
    if (!filePath || !textToInsert) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const edit = new vscode.WorkspaceEdit();

        try {
            await vscode.workspace.fs.stat(uri);
        } catch {
            // File does not exist, so we create it
            edit.createFile(uri);
        }

        let position = new vscode.Position(line, character);
        try {
            const doc = await vscode.workspace.openTextDocument(uri);
            if (character > 0 && line < doc.lineCount) {
                const linePrefix = doc.lineAt(line).text.substring(0, character);
                if (linePrefix.trim() === '' && /^\\s/.test(textToInsert)) {
                    // Replace the existing whitespace prefix with the one from textToInsert
                    edit.replace(uri, new vscode.Range(new vscode.Position(line, 0), position), textToInsert);
                    return {
                        edit: edit,
                        successMessage: `Successfully inserted code at ${vscode.workspace.asRelativePath(uri)}:${line + 1}:${character + 1}`
                    };
                }
            }
        } catch (e) {
            // Ignore document open errors
        }

        edit.insert(uri, position, textToInsert);

        return {
            edit: edit,
            successMessage: `Successfully inserted code at ${vscode.workspace.asRelativePath(uri)}:${line + 1}:${character + 1}`
        };
    } catch (e) {
        return `Error inserting code: ${e.message}`;
    }
}

module.exports = insertCode;
