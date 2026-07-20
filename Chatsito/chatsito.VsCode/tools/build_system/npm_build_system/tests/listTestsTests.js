const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const listTests = require('../listTests.js');

describe('listTests Tool', function () {
    this.timeout(20000);

    it('should successfully discover tests in project', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_listtests');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const testFile = path.join(testDir, 'dummy.test.js');
        const testCode = `
describe("My Dummy Suite", () => {
    it("should pass this test", () => {
        assert.ok(true);
    });
});
`;
        fs.writeFileSync(testFile, testCode, 'utf8');
        
        const output = await listTests(testDir);
        
        assert.ok(output.includes('Discovered Tests'), `Output: ${output}`);
        assert.ok(output.includes('My Dummy Suite'), 'Should capture suite name');
        assert.ok(output.includes('should pass this test'), 'Should capture test name');
        assert.ok(output.includes('dummy.test.js:3'), 'Should capture file name and line number');
        
        fs.unlinkSync(testFile);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await listTests('');
        assert.strictEqual(output, 'Error: Missing projectPath parameter.');
    });
});
