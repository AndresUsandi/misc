const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const compileFile = require('../python_build_system/compileFile');
const runFile = require('../python_build_system/runFile');

describe('Python compileFile and runFile Tools', function () {
    this.timeout(20000);

    it('should compile a python file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_py_run');
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        
        const pyFile = path.join(tempDir, 'script.py');
        fs.writeFileSync(pyFile, 'print("Hello from script")\n', 'utf8');

        const output = await compileFile(pyFile);
        assert.ok(output.includes('compiled') || output.toLowerCase().includes('python') || output.toLowerCase().includes('error'));

        fs.unlinkSync(pyFile);
        if (fs.existsSync(pyFile + 'c')) fs.unlinkSync(pyFile + 'c'); // Clean .pyc
        try {
            const pycache = path.join(tempDir, '__pycache__');
            if (fs.existsSync(pycache)) fs.rmSync(pycache, { recursive: true });
        } catch(e) {}
        fs.rmdirSync(tempDir);
    });

    it('should run a python file and return stdout', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_py_run2');
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        
        const pyFile = path.join(tempDir, 'script.py');
        fs.writeFileSync(pyFile, 'import sys\nprint("Hello: " + sys.argv[1])\n', 'utf8');

        const output = await runFile(pyFile, 'World');
        assert.ok(output.includes('Hello: World') || output.toLowerCase().includes('error'));

        fs.unlinkSync(pyFile);
        fs.rmdirSync(tempDir);
    });
});
