const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const PatchManager = require('../../../PatchManager.js');

describe('moveFile Tool', function () {
    this.timeout(20000);

    it('should successfully move a file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const sourcePath = path.join(root, 'test', 'fixtures', 'MoveSource.js');
        const destPath = path.join(root, 'test', 'fixtures', 'MoveDest.js');
        
        fs.writeFileSync(sourcePath, 'console.log("move me");', 'utf8');
        if (fs.existsSync(destPath)) fs.unlinkSync(destPath);
        
        const args = {
            source_path: sourcePath,
            dest_path: destPath
        };
        const output = await PatchManager.executeTool('move_file', args);
        
        assert.ok(typeof output === 'string' && output.includes('Successfully moved/renamed'), `Should return success. Output: ${output}`);
        assert.ok(fs.existsSync(destPath), 'Destination file should exist');
        assert.ok(!fs.existsSync(sourcePath), 'Source file should not exist');
        
        fs.unlinkSync(destPath);
    });

    it('should return error for missing parameters', async () => {
        const output = await PatchManager.executeTool('move_file', {});
        assert.ok(output.includes('Missing required parameters'), `Output: ${output}`);
    });
});
