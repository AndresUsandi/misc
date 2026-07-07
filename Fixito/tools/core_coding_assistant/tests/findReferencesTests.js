const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const findReferences = require('../findReferences.js');

describe('findReferences Tool', function () {
    this.timeout(20000);

    it('should find references of a method in a JS file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Act: TargetMethod definition is at line 0, character 9
        const output = await findReferences(fixturePath, 0, 9);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('TestDefinition.js:6:5 -> TargetMethod()'), `Output should contain the reference. Output was: ${output}`);
    });

    it('should return error for empty file path', async () => {
        const output = await findReferences('', 0, 0);
        assert.strictEqual(output, 'Error: No file path provided.');
    });
});
