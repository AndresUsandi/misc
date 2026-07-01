const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function restoreSessionMemory() {
    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const memPath = path.join(rootPath, '.chatsito', 'memory.json');
        
        if (!fs.existsSync(memPath)) {
            return "No session memory found.";
        }

        const memObj = JSON.parse(fs.readFileSync(memPath, 'utf8'));
        
        if (!memObj.memory) {
            return "Session memory is empty.";
        }

        return `=== Restored Session Memory ===\nSaved At: ${memObj.savedAt}\n\n${memObj.memory}`;

    } catch (e) {
        return `Error restoring session memory: ${e.message}`;
    }
}

module.exports = restoreSessionMemory;
