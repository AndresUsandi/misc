const assert = require('assert');
const path = require('path');
const vscode = require('vscode');
const buildProject = require('../buildProject.js');

describe('buildProject Tool', function () {
    this.timeout(20000);

    it('should invoke dotnet build and return execution result', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const dummyPath = path.join(root, 'dummy.csproj');

        const output = await buildProject(dummyPath);
        
        assert.ok(output.includes(`Build Project: ${dummyPath}`), `Output: ${output}`);
        // If dotnet is installed, it will error about MSBuild project not found
        // If dotnet is NOT installed, it will say "dotnet: command not found" or "is not recognized"
        assert.ok(output.includes('MSB1003') || output.includes('MSB1009') || output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet output');
    });

    it('should return error for missing parameters', async () => {
        const output = await buildProject('');
        assert.strictEqual(output, 'Error: No project path provided.');
    });
});
