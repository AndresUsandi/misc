const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const { getContextAtLocation } = require('../getContextAtLocation.js');

describe('getContextAtLocation Tool', function () {
    this.timeout(20000);

    it('should find enclosing symbol and its call stack context in a JS file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Act: Inside TargetMethod at line 1
        const output = await getContextAtLocation(fixturePath, 1, 5, 1);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('--- original context ---'), 'Should include original context');
        assert.ok(output.includes('TargetMethod'), 'Should mention TargetMethod as enclosing symbol');
        assert.ok(output.includes('--- invocation stack level 1 ---'), 'Should include caller context');
        assert.ok(output.includes('CallerMethod'), 'Should mention CallerMethod as caller');
    });

    it('should return error for empty file path', async () => {
        const output = await getContextAtLocation('', 0, 0);
        assert.strictEqual(output, 'Error: No file path provided.');
    });
});
