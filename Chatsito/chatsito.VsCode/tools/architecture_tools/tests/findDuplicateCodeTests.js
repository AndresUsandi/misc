const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const findDuplicateCode = require('../findDuplicateCode.js');

describe('findDuplicateCode Tool', function () {
    this.timeout(20000);

    it('should detect duplicated code chunks', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_duplicates');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const chunk = `function complexMath(a, b) {\n    let sum = a + b;\n    let diff = a - b;\n    let prod = a * b;\n    let quot = a / b;\n    return sum + diff + prod + quot;\n}\n`;
        fs.writeFileSync(path.join(testDir, 'file1.js'), chunk + 'console.log(1);\n', 'utf8');
        fs.writeFileSync(path.join(testDir, 'file2.js'), chunk + 'console.log(2);\n', 'utf8');
        
        const output = await findDuplicateCode(testDir);
        
        assert.ok(output.includes('Duplicate Code Found'), `Output: ${output}`);
        assert.ok(output.includes('file1.js'), 'Should flag file1.js');
        assert.ok(output.includes('file2.js'), 'Should flag file2.js');
        
        fs.unlinkSync(path.join(testDir, 'file1.js'));
        fs.unlinkSync(path.join(testDir, 'file2.js'));
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await findDuplicateCode('');
        assert.strictEqual(output, 'Error: Missing directory parameter.');
    });
});
