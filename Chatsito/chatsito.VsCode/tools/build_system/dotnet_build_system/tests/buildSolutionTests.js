const assert = require('assert');
const vscode = require('vscode');
const buildSolution = require('../buildSolution.js');

describe('buildSolution Tool', function () {
    this.timeout(20000);

    it('should invoke dotnet build without args and return execution result', async () => {
        const output = await buildSolution();
        
        assert.ok(output.includes('Build Solution'), `Output: ${output}`);
        // If dotnet is installed, it will error about MSBuild project not found
        // If dotnet is NOT installed, it will say "dotnet: command not found" or "is not recognized"
        assert.ok(output.includes('MSB1003') || output.includes('MSB1009') || output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet output');
    });
});
