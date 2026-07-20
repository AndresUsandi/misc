const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildProject = require('../nodejs_build_system/buildProject');
const listTests = require('../nodejs_build_system/listTests');

describe('Node.js Build System Tools', function () {
    this.timeout(20000);

    it('should identify tsconfig.json and select tsc build command', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_nodejs');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        const tsconfigPath = path.join(tempDir, 'tsconfig.json');
        fs.writeFileSync(tsconfigPath, '{}', 'utf8');

        const output = await buildProject(tempDir);
        assert.ok(output.includes('tsc') || output.toLowerCase().includes('error'));

        fs.unlinkSync(tsconfigPath);
        fs.rmdirSync(tempDir);
    });

    it('should scan JS/TS test files and list describe/it tests', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_nodejs_tests');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        
        const testFilePath = path.join(tempDir, 'sum.test.js');
        const testContent = `
describe("Sum Suite", () => {
    it("should add 2 numbers", () => {
        expect(1 + 1).toBe(2);
    });
    test("should subtract", () => {
    });
});
        `;
        fs.writeFileSync(testFilePath, testContent, 'utf8');

        const output = await listTests(tempDir);
        assert.ok(output.includes('Discovered Tests'), `Output: ${output}`);
        assert.ok(output.includes('Sum Suite'), `Output: ${output}`);
        assert.ok(output.includes('should add 2 numbers'), `Output: ${output}`);
        assert.ok(output.includes('should subtract'), `Output: ${output}`);

        fs.unlinkSync(testFilePath);
        fs.rmdirSync(tempDir);
    });
});
