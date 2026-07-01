const assert = require('assert');
const vscode = require('vscode');
const listWorkspaceFiles = require('../listWorkspaceFiles.js');

describe('listWorkspaceFiles Tool', function () {
    this.timeout(10000);

    before(async () => {
        // Wait for VS Code indexing to settle
        await new Promise(resolve => setTimeout(resolve, 3000));
    });

    it('should list all workspace files when no filter is provided', async () => {
        const output = await listWorkspaceFiles();
        console.log("DEBUG listWorkspaceFiles output:", output);
        assert.ok(output.includes('=== Workspace Files'), 'Should contain workspace files header');
        assert.ok(output.includes('package.json'), 'Should find package.json');
        assert.ok(output.includes('extension.js'), 'Should find extension.js');
    });

    it('should list matching files when filter is provided', async () => {
        const output = await listWorkspaceFiles('**/*.json');
        assert.ok(output.includes('=== Workspace Files'), 'Should contain header');
        assert.ok(output.includes('package.json'), 'Should find package.json');
        assert.ok(!output.includes('extension.js'), 'Should not contain extension.js');
    });

    it('should handle no files found', async () => {
        const output = await listWorkspaceFiles('**/nonexistent_pattern_xyz_123.abc');
        assert.strictEqual(output, 'No files found in workspace matching pattern: **/nonexistent_pattern_xyz_123.abc');
    });
});
