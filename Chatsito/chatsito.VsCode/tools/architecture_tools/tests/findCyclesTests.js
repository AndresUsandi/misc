const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const findCycles = require('../findCycles.js');

describe('findCycles Tool', function () {
    this.timeout(20000);

    it('should detect circular dependencies', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_cycles');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        fs.writeFileSync(path.join(testDir, 'a.js'), 'require("./b.js");', 'utf8');
        fs.writeFileSync(path.join(testDir, 'b.js'), 'require("./c.js");', 'utf8');
        fs.writeFileSync(path.join(testDir, 'c.js'), 'require("./a.js");', 'utf8');
        
        const output = await findCycles(testDir);
        
        assert.ok(output.includes('Circular Dependencies Found'), `Output: ${output}`);
        assert.ok(output.includes('a.js'), 'Should include a.js');
        assert.ok(output.includes('b.js'), 'Should include b.js');
        assert.ok(output.includes('c.js'), 'Should include c.js');
        
        fs.unlinkSync(path.join(testDir, 'a.js'));
        fs.unlinkSync(path.join(testDir, 'b.js'));
        fs.unlinkSync(path.join(testDir, 'c.js'));
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await findCycles('');
        assert.strictEqual(output, 'Error: Missing directory parameter.');
    });
});
