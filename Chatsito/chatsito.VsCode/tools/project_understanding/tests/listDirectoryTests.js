const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const listDirectory = require('../listDirectory.js');

describe('listDirectory Tool', () => {
    it('should list the workspace root when path is empty or undefined', async () => {
        const output = await listDirectory('');
        assert.ok(output.includes('=== Directory Contents:'), 'Should contain the header');
        assert.ok(output.includes('package.json'), 'Should include package.json in the list');
        assert.ok(output.includes('tools/'), 'Should list directories like tools/');
    });

    it('should list a specific relative directory', async () => {
        const output = await listDirectory('test/fixtures');
        assert.ok(output.includes('=== Directory Contents: test/fixtures ==='), `Header missing or wrong: ${output}`);
        assert.ok(output.includes('TestDefinition.js'), 'Should include TestDefinition.js');
    });

    it('should list a specific absolute directory', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0);
        const absPath = path.resolve(workspaceFolders[0].uri.fsPath, 'test/fixtures');
        const output = await listDirectory(absPath);
        assert.ok(output.includes('=== Directory Contents: test/fixtures ==='), `Header missing or wrong: ${output}`);
        assert.ok(output.includes('TestDefinition.js'), 'Should include TestDefinition.js');
    });

    it('should return error for non-existent path', async () => {
        const output = await listDirectory('non-existent-directory-abc-123');
        assert.ok(output.includes('Error: Directory does not exist'), `Expected error message, got: ${output}`);
    });

    it('should return error if path is a file', async () => {
        const output = await listDirectory('package.json');
        assert.ok(output.includes('Error: Path is not a directory'), `Expected not a directory error, got: ${output}`);
    });
});
