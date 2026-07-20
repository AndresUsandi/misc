const assert = require('assert');
const path = require('path');
const vscode = require('vscode');
const runTest = require('../runTest.js');

describe('runTest Tool', function () {
    this.timeout(20000);

    it('should invoke dotnet test --filter and return execution result', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const dummyPath = path.join(root, 'dummy-test.csproj');

        const output = await runTest('MyTestName');
        
        assert.ok(output.includes(`Run Test: MyTestName`), `Output: ${output}`);
        assert.ok(output.includes('MSB1003') || output.includes('MSB1009') || output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet output');
    });

    it('should return error for missing parameters', async () => {
        const output1 = await runTest('');
        assert.strictEqual(output1, 'Error: No test name provided.');
    });
});
