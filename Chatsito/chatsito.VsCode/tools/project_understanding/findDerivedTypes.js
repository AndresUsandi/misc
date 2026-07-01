const vscode = require('vscode');
const path = require('path');

async function findDerivedTypes(filePath, line, character) {
    let uri;
    let position;

    try {
        if (filePath && typeof line === 'number' && typeof character === 'number') {
            if (path.isAbsolute(filePath)) {
                uri = vscode.Uri.file(filePath);
            } else {
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (workspaceFolders && workspaceFolders.length > 0) {
                    uri = vscode.Uri.file(path.resolve(workspaceFolders[0].uri.fsPath, filePath));
                } else {
                    return `Error: Could not resolve relative path '${filePath}' because no workspace folders are open.`;
                }
            }
            position = new vscode.Position(line, character);
        } else {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                return "Error: No active editor and no location provided.";
            }
            uri = editor.document.uri;
            position = editor.selection.active;
        }

        await vscode.workspace.openTextDocument(uri);

        const items = await vscode.commands.executeCommand('vscode.prepareTypeHierarchy', uri, position) || [];
        const itemList = (Array.isArray(items) ? items : (items ? [items] : [])).filter(Boolean);

        if (itemList.length === 0) {
            return `No type hierarchy found at ${vscode.workspace.asRelativePath(uri)}:${position.line + 1}:${position.character + 1}`;
        }

        let output = `=== Derived Types / Subtypes ===\n\n`;
        for (const item of itemList) {
            output += `Type: ${item.name} (${vscode.SymbolKind[item.kind] || 'Type'})\n`;
            output += `  Declared at: ${vscode.workspace.asRelativePath(item.uri)}:${item.range.start.line + 1}\n`;

            const subtypes = await vscode.commands.executeCommand('vscode.provideSubtypes', item) || [];
            if (subtypes.length > 0) {
                output += `  Derived Types:\n`;
                for (const sub of subtypes) {
                    output += `    - ${sub.name} (${vscode.workspace.asRelativePath(sub.uri)}:${sub.range.start.line + 1})\n`;
                }
            } else {
                output += `  No derived types found.\n`;
            }
            output += '\n';
        }

        return output.trim();
    } catch (error) {
        return `Error finding derived types: ${error.message}`;
    }
}

module.exports = findDerivedTypes;
