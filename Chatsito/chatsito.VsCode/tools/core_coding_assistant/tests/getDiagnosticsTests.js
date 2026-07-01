const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const getDiagnostics = require('../getDiagnostics.js');

describe('getDiagnostics Tool', function () {
    this.timeout(20000);

    it('should return diagnostics for the workspace', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        
        // Let the language server process the file
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const output = await getDiagnostics(fixturePath);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(typeof output === 'string', 'Output should be a string');
        // Might be "No errors or warnings found" or "=== Diagnostics"
    });

    it('should return diagnostics for all files when no file is provided', async () => {
        const output = await getDiagnostics();
        assert.ok(output, 'Output should not be null');
        assert.ok(typeof output === 'string', 'Output should be a string');
    });
});
