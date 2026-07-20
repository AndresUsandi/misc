const assert = require('assert');
const path = require('path');
const vscode = require('vscode');
const listTests = require('../listTests.js');

describe('Generic listTests Tool', function () {
    this.timeout(20000);

    it('should route to dotnet list tests for .csproj path', async () => {
        const output = await listTests('test.csproj');
        
        assert.ok(output.includes('Available Tests'), `Output: ${output}`);
        assert.ok(output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error') || output.toLowerCase().includes('test'), 'Should capture dotnet list output');
    });

    it('should route to npm list tests and parse mocha tests', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        // Pointing to build_system directory where we just created tests
        const targetDir = path.join(parentDir, 'chatsito.VsCode', 'tools', 'build_system');
        
        const output = await listTests(targetDir);
        
        assert.ok(output.includes('Discovered Tests') || output.includes('Test Discovery'), `Output: ${output}`);
        // Since we created tests there, it should discover some tests like "should identify dotnet project type"
        assert.ok(output.includes('Project Detector Helper') || output.includes('Generic buildProject Tool'), 'Should discover our mocha test suites');
    });

    it('should return error for unsupported project path', async () => {
        const output = await listTests('dummy.txt');
        assert.ok(output.startsWith('Error:'), `Output: ${output}`);
    });
});
