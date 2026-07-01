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

    afterEach(() => {
        if (fs.existsSync(testFilePath)) {
            fs.unlinkSync(testFilePath);
        }
    });

    it('should successfully execute a valid replace modification', async () => {
        const args = {
            file_path: testFilePath,
            start_line: 2,
            start_char: 12,
            end_line: 2,
            end_char: 19,
            text_to_replace: '"moon"',
            expected_original_text: '"world"'
        };
        
        const result = await PatchManager.executeTool('replace_code', args);

        assert.ok(typeof result === 'string', 'Should return a success string');
        assert.ok(result.includes('Successfully replaced'), `Actual result: ${result}`);
        assert.strictEqual(PatchManager.patchHistory.length, 1);
        
        const content = fs.readFileSync(testFilePath, 'utf8');
        assert.ok(content.includes('return "moon"'));
    });

    it('should fail executeTool if stale edit is detected', async () => {
        const args = {
            file_path: testFilePath,
            start_line: 2,
            start_char: 12,
            end_line: 2,
            end_char: 19,
            text_to_replace: '"moon"',
            expected_original_text: '"stale"'
        };
        
        const result = await PatchManager.executeTool('replace_code', args);

        assert.ok(result.includes('Stale edit detected'));
        assert.strictEqual(PatchManager.patchHistory.length, 0);
    });

    it('should handle unknown modification types gracefully', async () => {
        const result = await PatchManager.executeTool('unknown_tool', {});
        assert.ok(result.includes('Unknown patch tool'));
    });
});
