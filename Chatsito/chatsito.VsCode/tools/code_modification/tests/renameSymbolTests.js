const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('renameSymbol Tool', function () {
    this.timeout(20000);

    it('should successfully rename a symbol', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'RenameCodeFixture.js');
        
        fs.writeFileSync(fixturePath, 'function myFunc() {}\nmyFunc();\n', 'utf8');
        
        // Let language server process
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const args = {
            file_path: fixturePath,
            line: 1,
            character: 11,
            new_name: 'newName'
        };
        const output = await PatchManager.executeTool('rename_symbol', args);
        
        assert.ok(typeof output === 'string' && output.includes('Successfully renamed'), `Should return success. Output: ${output}`);
        
        const newContent = fs.readFileSync(fixturePath, 'utf8');
        assert.ok(newContent.includes('function newName()'), 'Declaration should be renamed');
        assert.ok(newContent.includes('newName();'), 'Invocation should be renamed');
        
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await PatchManager.executeTool('rename_symbol', {});
        assert.ok(output.includes('Missing required parameters'), `Output: ${output}`);
    });
});
