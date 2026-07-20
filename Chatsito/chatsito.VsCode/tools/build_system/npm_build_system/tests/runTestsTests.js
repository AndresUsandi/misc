const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const runTests = require('../runTests.js');

describe('runTests Tool', function () {
    this.timeout(20000);

    it('should successfully run tests in the project', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_runtests');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-runtests",
            scripts: { "test": "node -e \"console.log('MOCK TESTS PASSED')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await runTests(testDir);
        
        assert.ok(output.includes('Test Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK TESTS PASSED'), 'Should capture stdout of test command');
        assert.ok(output.includes('All tests passed successfully'), 'Should report success');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await runTests('');
        assert.strictEqual(output, 'Error: Missing projectPath parameter.');
    });
});
