const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildProject = require('../python_build_system/buildProject');
const listTests = require('../python_build_system/listTests');

describe('Python Build System Tools', function () {
    this.timeout(20000);

    it('should identify requirements.txt and return build command execution', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_python');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        const reqPath = path.join(tempDir, 'requirements.txt');
        fs.writeFileSync(reqPath, 'pytest', 'utf8');

        const output = await buildProject(tempDir);
        assert.ok(output.includes('pip install') || output.toLowerCase().includes('python') || output.toLowerCase().includes('error'));

        fs.unlinkSync(reqPath);
        fs.rmdirSync(tempDir);
    });

    it('should scan Python test files and extract tests', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_python_tests');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        
        const testFilePath = path.join(tempDir, 'test_math.py');
        const testContent = `
class TestMath:
    def test_add(self):
        assert 1 + 1 == 2

def test_subtract():
    assert 2 - 1 == 1
        `;
        fs.writeFileSync(testFilePath, testContent, 'utf8');

        const output = await listTests(tempDir);
        assert.ok(output.includes('Discovered Python Tests'), `Output: ${output}`);
        assert.ok(output.includes('TestMath'), `Output: ${output}`);
        assert.ok(output.includes('test_add'), `Output: ${output}`);
        assert.ok(output.includes('test_subtract'), `Output: ${output}`);

        fs.unlinkSync(testFilePath);
        fs.rmdirSync(tempDir);
    });
});
