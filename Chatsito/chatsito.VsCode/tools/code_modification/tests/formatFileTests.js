const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('formatFile Tool', function () {
    this.timeout(20000);

    it('should successfully format a file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'FormatFixture.js');
        
        fs.writeFileSync(fixturePath, 'function test(){\nconsole.log("unformatted");\n}\n', 'utf8');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const args = { filePath: fixturePath };
        const output = await PatchManager.executeTool('formatFile', args);
        
        assert.ok(typeof output === 'string' && (output.includes('Successfully formatted') || output.includes('No formatting changes')), `Output: ${output}`);
        
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await PatchManager.executeTool('formatFile', {});
        assert.ok(output.includes('Missing required parameters'), `Output: ${output}`);
    });
});
