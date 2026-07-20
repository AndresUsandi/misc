const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const runTests = require('../runTests.js');

describe('Generic runTests Tool', function () {
    this.timeout(20000);

    it('should route to dotnet run tests for dotnet paths', async () => {
        const output = await runTests('test.csproj');
        
        assert.ok(output.includes('Run Tests'), `Output: ${output}`);
        assert.ok(output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet execution or error');
    });

    it('should route to npm run tests for npm paths', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_run_tests_generic');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-run-tests-generic",
            scripts: { "test": "node -e \"console.log('MOCK ALL TESTS RUN SUCCESS')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await runTests(testDir);
        
        assert.ok(output.includes('Test Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK ALL TESTS RUN SUCCESS'), 'Should capture stdout of tests run command');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for unsupported project path', async () => {
        const output = await runTests('dummy.txt');
        assert.ok(output.startsWith('Error:'), `Output: ${output}`);
    });
});
