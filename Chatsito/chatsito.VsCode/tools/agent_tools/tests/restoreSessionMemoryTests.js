const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const restoreSessionMemory = require('../restoreSessionMemory.js');
const saveSessionMemory = require('../saveSessionMemory.js');

describe('restoreSessionMemory Tool', function () {
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

    it('should successfully restore session memory', async () => {
        await saveSessionMemory('Previous memory string');
        const output = await restoreSessionMemory();
        assert.ok(output.includes('Restored Session Memory'), `Output: ${output}`);
        assert.ok(output.includes('Previous memory string'), 'Should contain the saved memory');
    });

    it('should return message if no memory is found', async () => {
        const output = await restoreSessionMemory();
        assert.strictEqual(output, 'No session memory found.');
    });
});
