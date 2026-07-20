const assert = require('assert');
const path = require('path');
const vscode = require('vscode');
const runTests = require('../runTests.js');

describe('runTests Tool', function () {
    this.timeout(20000);

    it('should invoke dotnet test and return execution result', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const dummyPath = path.join(root, 'dummy-test.csproj');

        const output = await runTests();
        
        assert.ok(output.includes(`Run Tests`), `Output: ${output}`);
        assert.ok(output.includes('MSB1003') || output.includes('MSB1009') || output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet output');
    });
});
