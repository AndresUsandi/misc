const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const findDefinition = require('../findDefinition.js');

describe('findDefinition Tool', function () {
    this.timeout(20000); // Give language server time to initialize

    it('should correctly find the definition of a method in a JS file', async () => {
        // Arrange
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');

        // Open and show the document so the language server registers it
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);

        // Wait for JS/TS extension / language server to load
        await new Promise(resolve => setTimeout(resolve, 5000));

        // Act: TargetMethod() is at line 6 (0-index 5), character 5
        const output = await findDefinition(fixturePath, 5, 5);

        // Assert
        assert.ok(output, 'Output should not be null');
        assert.ok(!output.includes('No definitions found'), `Definition should be found. Output was: ${output}`);

        // Check that it pointed to the right file and line (Line 1)
        assert.ok(output.includes('TestDefinition.js'), 'Should mention the target file');
        assert.ok(output.includes('Line: 1'), 'Should point to line 1 (the definition)');
    });

    it('should return error for empty file path', async () => {
        const output = await findDefinition('', 0, 0);
        assert.strictEqual(output, 'Error: No file path provided.');
    });
});
