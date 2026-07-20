const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('insertCode Tool', function () {
    this.timeout(20000);

    it('should successfully insert code at the specified position', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'InsertCodeFixture.js');
        
        // Setup initial fixture
        fs.writeFileSync(fixturePath, 'function test() {\n}\n', 'utf8');
        
        const args = {
            filePath: fixturePath,
            line: 1,
            character: 18,
            textToInsert: '\n    console.log("inserted!");'
        };
        const output = await PatchManager.executeTool('insertCode', args);
        
        assert.ok(typeof output === 'string' && output.includes('Successfully inserted'), `Should return success. Output: ${output}`);
        
        // Verify file content
        const newContent = fs.readFileSync(fixturePath, 'utf8');
        assert.ok(newContent.includes('console.log("inserted!");'), 'Content should contain inserted text');
        
        // Cleanup
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await PatchManager.executeTool('insertCode', {});
        assert.ok(output.includes('Missing required parameters'), `Output: ${output}`);
    });
});
