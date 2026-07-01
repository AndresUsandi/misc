const vscode = require('vscode');
const path = require('path');

async function moveType(filePath, typeName, destFilePath) {
    if (!filePath || !typeName || !destFilePath) return "Error: Missing required parameters.";

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));

        const doc = await vscode.workspace.openTextDocument(uri);
        const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];
        
        let typeSymbol = symbols.find(s => s.name === typeName && (s.kind === vscode.SymbolKind.Class || s.kind === vscode.SymbolKind.Interface || s.kind === vscode.SymbolKind.Struct || s.kind === vscode.SymbolKind.Enum));
        if (!typeSymbol) {
            return `Error: Could not find type '${typeName}' in ${vscode.workspace.asRelativePath(uri)}. Manual move may be required.`;
        }

        const codeActions = await vscode.commands.executeCommand('vscode.executeCodeActionProvider', uri, typeSymbol.selectionRange) || [];
        const moveAction = codeActions.find(a => a.title.toLowerCase().includes('move') && a.title.toLowerCase().includes('file'));
        if (moveAction && moveAction.edit) {
            return {
                edit: moveAction.edit,
                successMessage: `Successfully applied move refactoring for type '${typeName}'.`
            };
        } else {
            // Note: Many languages don't support automated Move Type via Code Actions headless
            return `No automated move refactoring available for type '${typeName}'. Please move it manually.`;
        }
    } catch (e) {
        return `Error moving type: ${e.message}`;
    }
}

module.exports = moveType;
