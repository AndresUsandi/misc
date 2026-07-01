const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function saveSessionMemory(memoryString) {
    if (!memoryString) return "Error: Missing memoryString parameter.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const chatsitoDir = path.join(rootPath, '.chatsito');
        
        if (!fs.existsSync(chatsitoDir)) {
            fs.mkdirSync(chatsitoDir, { recursive: true });
        }

        const memPath = path.join(chatsitoDir, 'memory.json');
        
        const memObj = {
            savedAt: new Date().toISOString(),
            memory: String(memoryString)
        };

        fs.writeFileSync(memPath, JSON.stringify(memObj, null, 2), 'utf8');

        return `Session memory saved successfully.`;

    } catch (e) {
        return `Error saving session memory: ${e.message}`;
    }
}

module.exports = saveSessionMemory;
