const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildProject = require('../buildProject.js');

describe('Generic buildProject Tool', function () {
    this.timeout(20000);

    it('should route to dotnet build Project for csproj extension', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const dummyPath = path.join(root, 'dummy.csproj');

        const output = await buildProject(dummyPath);
        
        assert.ok(output.includes(`Build Project: ${dummyPath}`), `Output: ${output}`);
        assert.ok(output.includes('MSB1003') || output.includes('MSB1009') || output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet output');
    });

    it('should route to npm build Project for package.json directory', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_build_generic');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-build-proj-generic",
            scripts: { "build": "node -e \"console.log('MOCK BUILD SUCCESS GENERIC')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await buildProject(testDir);
        
        assert.ok(output.includes('Build Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK BUILD SUCCESS GENERIC'), 'Should capture stdout of build command');
        assert.ok(output.includes('Build succeeded'), 'Should report success');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for unsupported project path', async () => {
        const output = await buildProject('dummy.txt');
        assert.ok(output.startsWith('Error:'), `Output: ${output}`);
    });
});
