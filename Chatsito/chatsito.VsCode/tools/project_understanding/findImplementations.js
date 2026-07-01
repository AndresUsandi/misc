const vscode = require('vscode');
const path = require('path');

async function findImplementations(filePath, line, character) {
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

        const implementations = await vscode.commands.executeCommand('vscode.executeImplementationProvider', uri, position) || [];
        
        const list = Array.isArray(implementations) ? implementations : [implementations];
        if (list.length === 0) {
            return `No implementations found for symbol at ${vscode.workspace.asRelativePath(uri)}:${position.line + 1}:${position.character + 1}`;
        }

        let output = `=== Implementations Found (${list.length} matches) ===\n\n`;
        for (const impl of list) {
            const targetUri = impl.uri || impl.targetUri;
            const targetRange = impl.range || impl.targetRange;
            if (targetUri && targetRange) {
                const relPath = vscode.workspace.asRelativePath(targetUri);
                let lineText = '';
                try {
                    const doc = await vscode.workspace.openTextDocument(targetUri);
                    lineText = doc.lineAt(targetRange.start.line).text.trim();
                } catch (_) {}
                
                output += `${relPath}:${targetRange.start.line + 1}:${targetRange.start.character + 1}`;
                if (lineText) {
                    output += ` -> ${lineText}`;
                }
                output += '\n';
            }
        }

        return output.trim();
    } catch (error) {
        return `Error finding implementations: ${error.message}`;
    }
}

module.exports = findImplementations;
