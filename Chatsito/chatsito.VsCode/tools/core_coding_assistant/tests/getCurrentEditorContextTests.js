const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const getCurrentEditorContext = require('../getCurrentEditorContext.js');

describe('getCurrentEditorContext Tool', function () {
    this.timeout(20000);

    it('should get the context of the active text editor', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        
        // Ensure cursor is somewhere in the file
        const editor = vscode.window.activeTextEditor;
        editor.selection = new vscode.Selection(new vscode.Position(1, 0), new vscode.Position(1, 0));

        const output = await getCurrentEditorContext(5, 5);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('TestDefinition.js'), 'Should include the active file path');
        assert.ok(output.includes('TargetMethod'), 'Should include code context');
    });

    it('should return a message when no editor is active', async () => {
        await vscode.commands.executeCommand('workbench.action.closeAllEditors');
        const output = await getCurrentEditorContext();
        assert.strictEqual(output, 'No active editor found.');
    });
});
