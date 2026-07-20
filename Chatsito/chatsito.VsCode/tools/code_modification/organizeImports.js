const vscode = require('vscode');
const path = require('path');
const { validateRequiredParams } = require('./codeUtils');

async function organizeImports(args) {
    let filePath;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ filePath } = args);
    } else {
        filePath = arguments[0];
    }

    const normalizedArgs = { filePath };
    const validationErr = validateRequiredParams("organizeImports", normalizedArgs);
    if (validationErr) {
        return validationErr;
    }

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const doc = await vscode.workspace.openTextDocument(uri);
        const range = new vscode.Range(new vscode.Position(0, 0), new vscode.Position(doc.lineCount, 0));
        
        const codeActions = await vscode.commands.executeCommand('vscode.executeCodeActionProvider', uri, range, vscode.CodeActionKind.SourceOrganizeImports.value) || [];
        
        const organizeAction = codeActions.find(a => (a.kind && a.kind.value === 'source.organizeImports') || a.title.toLowerCase().includes('organize imports'));
        
        if (organizeAction) {
            if (organizeAction.edit) {
                return {
                    edit: organizeAction.edit,
                    successMessage: `Successfully organized imports in ${vscode.workspace.asRelativePath(uri)}.`
                };
            } else if (organizeAction.command) {
                return {
                    command: organizeAction.command.command,
                    args: organizeAction.command.arguments || [],
                    successMessage: `Executed organize imports command.`
                };
            }
        }
        
        return `No organize imports provider available for this file, or no imports to organize.`;
    } catch (e) {
        return `Error organizing imports: ${e.message}`;
    }
}

module.exports = organizeImports;
