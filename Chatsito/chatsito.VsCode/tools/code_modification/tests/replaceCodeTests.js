const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('replaceCode Tool', function () {
    this.timeout(20000);

    it('should successfully replace code at the specified range', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'ReplaceCodeFixture.js');
        
        fs.writeFileSync(fixturePath, 'function test() {\n    return old;\n}\n', 'utf8');
        
        const args = {
            filePath: fixturePath,
            startLine: 2,
            startChar: 12,
            endLine: 2,
            endChar: 15,
            textToReplace: 'new',
            expectedOriginalText: 'old'
        };
        const output = await PatchManager.executeTool('replaceCode', args);
        
        assert.ok(typeof output === 'string' && output.includes('Successfully replaced code'), `Should return success. Output: ${output}`);
        
        const newContent = fs.readFileSync(fixturePath, 'utf8');
        assert.ok(newContent.includes('return new;'), 'Content should contain replaced text');
        
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await PatchManager.executeTool('replaceCode', {});
        assert.ok(output.includes('Missing required parameters'), `Output: ${output}`);
    });

    it('should successfully replace code when startChar and endChar are omitted', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'ReplaceCodeLineFixture.js');
        
        fs.writeFileSync(fixturePath, 'function test() {\n    return old;\n}\n', 'utf8');
        
        const args = {
            filePath: fixturePath,
            startLine: 2,
            endLine: 2,
            textToReplace: '    return new;',
            expectedOriginalText: '    return old;'
        };
        const output = await PatchManager.executeTool('replaceCode', args);
        
        assert.ok(typeof output === 'string' && output.includes('Successfully replaced code'), `Should return success. Output: ${output}`);
        
        const newContent = fs.readFileSync(fixturePath, 'utf8');
        assert.ok(newContent.includes('return new;'), 'Content should contain replaced text');
        
        fs.unlinkSync(fixturePath);
    });
});
