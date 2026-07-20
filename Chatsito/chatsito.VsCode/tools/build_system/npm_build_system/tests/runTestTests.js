const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const runTest = require('../runTest.js');

describe('runTest Tool', function () {
    this.timeout(20000);

    it('should successfully run a specific test', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_runtest_specific');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const scriptPath = path.join(testDir, 'script.js');
        fs.writeFileSync(scriptPath, "console.log('MOCK SPECIFIC TEST PASSED');", 'utf8');

        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-runtest-specific",
            scripts: { "test": "node script.js" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await runTest(testDir, 'My Test Name');
        
        assert.ok(output.includes('Specific Test Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK SPECIFIC TEST PASSED'), 'Should capture stdout');
        assert.ok(output.includes("Test 'My Test Name' passed"), 'Should report success for specific test');
        
        fs.unlinkSync(pkgPath);
        fs.unlinkSync(scriptPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output1 = await runTest('');
        assert.strictEqual(output1, 'Error: Missing projectPath parameter.');
        const output2 = await runTest('path', '');
        assert.strictEqual(output2, 'Error: Missing testName parameter.');
    });
});
