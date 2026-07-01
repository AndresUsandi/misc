const vscode = require('vscode');
const path = require('path');

async function replaceCode(filePath, startLine, startChar, endLine, endChar, textToReplace) {
    if (!filePath || textToReplace === undefined) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        let startCharToUse = startChar;
        try {
            const doc = await vscode.workspace.openTextDocument(uri);
            if (startChar > 0 && startLine < doc.lineCount) {
                const linePrefix = doc.lineAt(startLine).text.substring(0, startChar);
                if (linePrefix.trim() === '' && /^\s/.test(textToReplace)) {
                    startCharToUse = 0;
                }
            }
        } catch (e) {
            // Document might not exist yet, ignore
        }

        const edit = new vscode.WorkspaceEdit();
        const range = new vscode.Range(new vscode.Position(startLine, startCharToUse), new vscode.Position(endLine, endChar));
        edit.replace(uri, range, textToReplace);
        
        return {
            edit: edit,
            successMessage: `Successfully replaced code at ${vscode.workspace.asRelativePath(uri)} from line ${startLine + 1} to ${endLine + 1}`
        };
    } catch (e) {
        return `Error replacing code: ${e.message}`;
    }
}

module.exports = replaceCode;
