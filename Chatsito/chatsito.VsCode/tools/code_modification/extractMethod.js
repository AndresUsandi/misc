const vscode = require('vscode');
const path = require('path');

async function extractMethod(filePath, startLine, startChar, endLine, endChar, newMethodName) {
    if (!filePath || !newMethodName) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const doc = await vscode.workspace.openTextDocument(uri);
        const range = new vscode.Range(new vscode.Position(startLine, startChar), new vscode.Position(endLine, endChar));
        
        const codeActions = await vscode.commands.executeCommand('vscode.executeCodeActionProvider', uri, range) || [];
        const extractAction = codeActions.find(a => a.title.toLowerCase().includes('extract') && (a.title.toLowerCase().includes('method') || a.title.toLowerCase().includes('function')));
        
        if (extractAction) {
            // Some refactorings execute commands directly instead of returning an edit
            if (extractAction.edit) {
                return {
                    edit: extractAction.edit,
                    successMessage: `Successfully applied extract method refactoring. Extracted method may need to be manually renamed to '${newMethodName}'.`
                };
            } else if (extractAction.command) {
                return {
                    command: extractAction.command.command,
                    args: extractAction.command.arguments || [],
                    successMessage: `Executed extract method command. You may need to rename the new method to '${newMethodName}'.`
                };
            }
        }
        
        return `No automated extract method refactoring available for the selected range.`;
    } catch (e) {
        return `Error extracting method: ${e.message}`;
    }
}

module.exports = extractMethod;
