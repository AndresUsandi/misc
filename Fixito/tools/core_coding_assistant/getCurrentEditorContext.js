import vscode from '../../vscode.js';

async function getCurrentEditorContext() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return "No active editor found.";
    }

    const document = editor.document;
    const selection = editor.selection;
    const cursorLine = selection.active.line;
    const selectedText = document.getText(selection);
    const relativePath = vscode.workspace.asRelativePath(document.uri);

    let result = `=== Current Editor Context ===\n`;
    result += `File: ${relativePath}\n`;
    result += `Cursor Line: ${cursorLine + 1}\n`;
    
    if (selectedText) {
        result += `Selected Text:\n"""\n${selectedText}\n"""\n`;
    } else {
        result += `Selected Text: (none)\n`;
    }

    const startLine = Math.max(0, cursorLine - 10);
    const endLine = Math.min(document.lineCount - 1, cursorLine + 10);
    result += `\nNearby Code (Lines ${startLine + 1} to ${endLine + 1}):\n`;
    
    for (let i = startLine; i <= endLine; i++) {
        const lineText = document.lineAt(i).text;
        const marker = (i === cursorLine) ? " > " : "   ";
        result += `${marker}${String(i + 1).padStart(4)}: ${lineText}\n`;
    }

    return result;
}

export default getCurrentEditorContext;
