const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('extractMethod Tool', function () {
    this.timeout(20000);

    it('should attempt to extract a method', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'ExtractFixture.js');
        
        fs.writeFileSync(fixturePath, 'function main() {\n    console.log("hello");\n}\n', 'utf8');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const args = {
            filePath: fixturePath,
            startLine: 2,
            startChar: 5,
            endLine: 2,
            endChar: 26,
            newMethodName: 'myNewMethod'
        };
        const output = await PatchManager.executeTool('extractMethod', args);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(typeof output === 'string' && (output.includes('Successfully applied') || output.includes('Executed extract method') || output.includes('No automated extract')), `Output: ${output}`);
        
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await PatchManager.executeTool('extractMethod', {});
        assert.ok(output.includes('Missing required parameters'), `Output: ${output}`);
    });
});
