const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const getSymbolsInFile = require('../getSymbolsInFile.js');

describe('getSymbolsInFile Tool', function () {
    this.timeout(20000);

    it('should return symbols for a JS file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        
        // Wait for language server
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const output = await getSymbolsInFile(fixturePath);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('TargetMethod'), 'Should find TargetMethod symbol');
        assert.ok(output.includes('CallerMethod'), 'Should find CallerMethod symbol');
    });

    it('should return error for empty file path', async () => {
        const output = await getSymbolsInFile('');
        assert.strictEqual(output, 'Error: No file path provided.');
    });
});
