const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('deleteCode Tool', function () {
    this.timeout(20000);

    it('should successfully delete code at the specified range', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'DeleteCodeFixture.js');
        
        fs.writeFileSync(fixturePath, 'function test() {\n    return old;\n}\n', 'utf8');
        
        const args = {
            filePath: fixturePath,
            startLine: 2,
            startChar: 11,
            endLine: 2,
            endChar: 15,
            expectedOriginalText: ' old'
        };
        const output = await PatchManager.executeTool('deleteCode', args);
        
        assert.ok(typeof output === 'string' && output.includes('Successfully deleted'), `Should return success. Output: ${output}`);
        
        const newContent = fs.readFileSync(fixturePath, 'utf8');
        assert.ok(newContent.includes('return;'), 'Content should contain deleted text');
        
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await PatchManager.executeTool('deleteCode', {});
        assert.ok(output.includes('Missing required parameters'), `Output: ${output}`);
    });
});
