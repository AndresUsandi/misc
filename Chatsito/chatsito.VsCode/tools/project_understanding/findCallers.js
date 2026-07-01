const vscode = require('vscode');
const path = require('path');

async function findCallers(filePath, line, character) {
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

        let output = `=== Callers / Incoming Calls ===\n\n`;
        for (const item of itemList) {
            output += `Symbol: ${item.name} (${vscode.SymbolKind[item.kind] || 'Function'})\n`;
            output += `  Location: ${vscode.workspace.asRelativePath(item.uri)}:${item.range.start.line + 1}\n`;

            const incoming = await vscode.commands.executeCommand('vscode.provideIncomingCalls', item) || [];
            if (incoming.length > 0) {
                output += `  Incoming Calls:\n`;
                for (const call of incoming) {
                    const fromItem = call.from;
                    const rangesStr = call.fromRanges.map(r => `line ${r.start.line + 1}`).join(', ');
                    output += `    - ${fromItem.name} (${vscode.workspace.asRelativePath(fromItem.uri)}:${fromItem.range.start.line + 1}) at: ${rangesStr}\n`;
                }
            } else {
                output += `  No incoming calls found.\n`;
            }
            output += '\n';
        }

        return output.trim();
    } catch (error) {
        return `Error finding callers: ${error.message}`;
    }
}

module.exports = findCallers;
