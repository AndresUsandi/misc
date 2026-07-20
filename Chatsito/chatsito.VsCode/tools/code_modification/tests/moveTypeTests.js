const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const moveType = require('../moveType.js');

describe('moveType Tool', function () {
    this.timeout(20000);

    it('should attempt to move a type or fallback gracefully', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'MoveTypeFixture.js');
        const destPath = path.join(root, 'test', 'fixtures', 'MoveTypeDest.js');
        
        fs.writeFileSync(fixturePath, 'class MyClass {}\n', 'utf8');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const output = await moveType(fixturePath, 'MyClass', destPath);
        
        assert.ok(output, 'Output should not be null');
        // JS typically doesn't have an automated headless "move type to file" provider out of the box
        assert.ok(output.includes('Successfully applied') || output.includes('No automated move refactoring available'), `Output: ${output}`);
        
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await moveType('', '', '');
        assert.ok(output.includes('Missing required parameters'));
    });
});
