const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const saveSessionMemory = require('../saveSessionMemory.js');

describe('saveSessionMemory Tool', function () {
    this.timeout(10000);

    let memPath;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const rootPath = workspaceFolders[0].uri.fsPath;
        memPath = path.join(rootPath, '.chatsito', 'memory.json');
    });

    afterEach(() => {
        if (fs.existsSync(memPath)) {
            fs.unlinkSync(memPath);
        }
    });

    it('should successfully save session memory', async () => {
        const output = await saveSessionMemory('This is my memory');
        assert.strictEqual(output, 'Session memory saved successfully.');
        
        const memObj = JSON.parse(fs.readFileSync(memPath, 'utf8'));
        assert.strictEqual(memObj.memory, 'This is my memory');
    });

    it('should return error for missing parameters', async () => {
        const output = await saveSessionMemory('');
        assert.strictEqual(output, 'Error: Missing memoryString parameter.');
    });
});
