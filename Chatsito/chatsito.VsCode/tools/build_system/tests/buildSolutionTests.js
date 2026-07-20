const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildSolution = require('../buildSolution.js');

describe('Generic buildSolution Tool', function () {
    this.timeout(20000);

    it('should route to dotnet build Solution for .sln extension', async () => {
        const output = await buildSolution('test.sln');
        
        assert.ok(output.includes('Build Solution'), `Output: ${output}`);
        // It runs dotnet build inside workspace root, which will either succeed or fail with dotnet errors.
        assert.ok(output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error') || output.includes('MSBuild') || output.includes('Build succeeded') || output.includes('Build failed'), 'Should capture dotnet build output');
    });

    it('should route to npm build Solution for package.json directory', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_build_sol_generic');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-build-sol-generic",
            scripts: { "build": "node -e \"console.log('MOCK SOLUTION SUCCESS GENERIC')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await buildSolution(testDir);
        
        assert.ok(output.includes('Build Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK SOLUTION SUCCESS GENERIC'), 'Should capture stdout of build command');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for unsupported project path', async () => {
        const output = await buildSolution('dummy.txt');
        assert.ok(output.startsWith('Error:'), `Output: ${output}`);
    });
});
