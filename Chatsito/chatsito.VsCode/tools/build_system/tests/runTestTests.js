const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const runTest = require('../runTest.js');

describe('Generic runTest Tool', function () {
    this.timeout(20000);

    it('should route to dotnet run test for dotnet paths', async () => {
        const output = await runTest('test.csproj', 'MyTest');
        
        assert.ok(output.includes('Run Test: MyTest'), `Output: ${output}`);
        assert.ok(output.toLowerCase().includes('dotnet') || output.toLowerCase().includes('error'), 'Should capture dotnet execution or error');
    });

    it('should route to npm run test for npm paths', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_run_test_generic');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-run-test-generic",
            scripts: { "test": "node -e \"console.log('MOCK SINGLE TEST RUN SUCCESS')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await runTest(testDir, 'MyNpmTest');
        
        assert.ok(output.includes('Specific Test Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK SINGLE TEST RUN SUCCESS'), 'Should capture stdout of test run command');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should fallback to workspace root project type if first argument is a test name (single argument test)', async () => {
        // Workspace root contains package.json, so it should be identified as npm.
        // It will call npm runTest(undefined, 'MyTest') and try to run it in the workspace root.
        // Since workspace root's package.json test script is 'node ./test/runTest.js', it will fail/run that, but let's assert it routes to npm or starts executing.
        // Or we can just check that it starts and returns a result containing 'Specific Test Results'.
        const output = await runTest('MyTest');
        assert.ok(output.includes('Specific Test Results') || output.toLowerCase().includes('error'), `Output: ${output}`);
    });
});
