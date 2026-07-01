const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const findDeadCode = require('../findDeadCode.js');

describe('findDeadCode Tool', function () {
    this.timeout(20000);

    it('should detect unused functions', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_deadcode');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const fixtureCode = `
class MyClass {
    usedMethod() { console.log('used'); }
    unusedMethod() { console.log('unused'); }
}
const m = new MyClass();
m.usedMethod();
`;
        fs.writeFileSync(path.join(testDir, 'main.js'), fixtureCode, 'utf8');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(path.join(testDir, 'main.js')));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const output = await findDeadCode(testDir);
        
        assert.ok(output.includes('Dead Code Found'), `Output: ${output}`);
        assert.ok(output.includes('unusedMethod'), 'Should flag unusedMethod as dead code');
        
        fs.unlinkSync(path.join(testDir, 'main.js'));
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await findDeadCode('');
        assert.strictEqual(output, 'Error: Missing directory parameter.');
    });
});
