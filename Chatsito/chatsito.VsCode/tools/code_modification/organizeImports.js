const vscode = require('vscode');
const path = require('path');

async function organizeImports(filePath) {
    if (!filePath) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const doc = await vscode.workspace.openTextDocument(uri);
        const range = new vscode.Range(new vscode.Position(0, 0), new vscode.Position(doc.lineCount, 0));
        
        // Execute Code Action provider for source.organizeImports
        const codeActions = await vscode.commands.executeCommand('vscode.executeCodeActionProvider', uri, range, vscode.CodeActionKind.SourceOrganizeImports.value) || [];
        
        // Sometimes the action is returned without kind filtering
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
