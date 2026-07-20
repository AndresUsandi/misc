const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('PatchManager', function () {
    this.timeout(20000);

    let testFilePath;
    
    before(async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        testFilePath = path.join(root, 'test', 'fixtures', 'PatchManagerFixture.js');
    });

    beforeEach(() => {
        fs.writeFileSync(testFilePath, 'function hello() {\n    return "world";\n}\n', 'utf8');
        PatchManager.patchHistory = [];
    });

    afterEach(async () => {
        await vscode.commands.executeCommand('workbench.action.closeAllEditors');
        await new Promise(resolve => setTimeout(resolve, 100));
        if (fs.existsSync(testFilePath)) {
            try {
                fs.unlinkSync(testFilePath);
            } catch (e) {
                // Ignore EPERM/busy during cleanup
            }
        }
    });

    it('should successfully execute a valid replace modification', async () => {
        const args = {
            filePath: testFilePath,
            startLine: 2,
            startChar: 12,
            endLine: 2,
            endChar: 19,
            textToReplace: '"moon"',
            expectedOriginalText: '"world"'
        };
        
        const result = await PatchManager.executeTool('replaceCode', args);

        assert.ok(typeof result === 'string', 'Should return a success string');
        assert.ok(result.includes('Successfully replaced'), `Actual result: ${result}`);
        assert.strictEqual(PatchManager.patchHistory.length, 1);
        
        const content = fs.readFileSync(testFilePath, 'utf8');
        assert.ok(content.includes('return "moon"'));
    });

    it('should fail executeTool if stale edit is detected', async () => {
        const args = {
            filePath: testFilePath,
            startLine: 2,
            startChar: 12,
            endLine: 2,
            endChar: 19,
            textToReplace: '"moon"',
            expectedOriginalText: '"stale"'
        };
        
        const result = await PatchManager.executeTool('replaceCode', args);

        assert.ok(result.includes('Stale edit detected'));
        assert.strictEqual(PatchManager.patchHistory.length, 0);
    });

    it('should handle unknown modification types gracefully', async () => {
        const result = await PatchManager.executeTool('unknown_tool', {});
        assert.ok(result.includes('Unknown patch tool'));
    });
});
