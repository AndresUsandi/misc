const vscode = require('vscode');
const path = require('path');

async function findCallees(filePath, line, character) {
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

        const items = await vscode.commands.executeCommand('vscode.prepareCallHierarchy', uri, position) || [];
        const itemList = (Array.isArray(items) ? items : (items ? [items] : [])).filter(Boolean);

        if (itemList.length === 0) {
            return `No call hierarchy found at ${vscode.workspace.asRelativePath(uri)}:${position.line + 1}:${position.character + 1}`;
        }

        let output = `=== Callees / Outgoing Calls ===\n\n`;
        for (const item of itemList) {
            output += `Symbol: ${item.name} (${vscode.SymbolKind[item.kind] || 'Function'})\n`;
            output += `  Location: ${vscode.workspace.asRelativePath(item.uri)}:${item.range.start.line + 1}\n`;

            const outgoing = await vscode.commands.executeCommand('vscode.provideOutgoingCalls', item) || [];
            if (outgoing.length > 0) {
                output += `  Outgoing Calls:\n`;
                for (const call of outgoing) {
                    const toItem = call.to;
                    const rangesStr = call.fromRanges.map(r => `line ${r.start.line + 1}`).join(', ');
                    output += `    - ${toItem.name} (${vscode.workspace.asRelativePath(toItem.uri)}:${toItem.range.start.line + 1}) at: ${rangesStr}\n`;
                }
            } else {
                output += `  No outgoing calls found.\n`;
            }
            output += '\n';
        }

        return output.trim();
    } catch (error) {
        return `Error finding callees: ${error.message}`;
    }
}

module.exports = findCallees;
