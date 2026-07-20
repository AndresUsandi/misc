const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const getCodeCoverage = require('../getCodeCoverage.js');

describe('Generic getCodeCoverage Tool', function () {
    this.timeout(20000);

    it('should route to dotnet code coverage for .csproj path', async () => {
        const output = await getCodeCoverage('test.csproj');
        
        assert.ok(output.includes('Code Coverage Collection'), `Output: ${output}`);
        assert.ok(output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error') || output.toLowerCase().includes('test'), 'Should capture dotnet test coverage output');
    });

    it('should route to npm code coverage for package.json directory', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_coverage_generic');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-coverage-generic",
            scripts: { "test": "node -e \"console.log('MOCK COVERAGE SUCCESS GENERIC')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await getCodeCoverage(testDir);
        
        assert.ok(output.includes('Code Coverage Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK COVERAGE SUCCESS GENERIC'), 'Should capture stdout of test coverage command');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for unsupported project path', async () => {
        const output = await getCodeCoverage('dummy.txt');
        assert.ok(output.startsWith('Error:'), `Output: ${output}`);
    });
});
