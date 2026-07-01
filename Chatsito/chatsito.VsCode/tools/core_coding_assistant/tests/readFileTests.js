const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const readFile = require('../readFile.js');

describe('readFile Tool', function () {
    this.timeout(20000);

    it('should read the content of an existing file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');
        
        const output = await readFile(fixturePath);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('=== File Content:'), 'Should include header');
        assert.ok(output.includes('TargetMethod'), 'Should include file content');
    });

    it('should return error for empty file path', async () => {
        const output = await readFile('');
        assert.strictEqual(output, 'Error: No file path provided.');
    });

    it('should return error for non-existent file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fakePath = path.join(root, 'does_not_exist.js');
        const output = await readFile(fakePath);
        assert.ok(output.includes('Error: File not found'), 'Should indicate file not found');
    });
});
