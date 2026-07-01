const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const summarizeFile = require('../summarizeFile.js');

describe('summarizeFile Tool', function () {
    this.timeout(10000);

    let testFile;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        testFile = path.join(workspaceFolders[0].uri.fsPath, 'test-summary.js');
        
        const content = `
const fs = require('fs');
import path from 'path';

class MyClass {
    constructor() {}
    public myMethod(a, b) {
        return a + b;
    }
}

function globalFunc() {
    console.log('hi');
}
`;
        fs.writeFileSync(testFile, content.trim());
    });

    after(() => {
        if (fs.existsSync(testFile)) fs.unlinkSync(testFile);
    });

    it('should successfully summarize a file', async () => {
        const output = await summarizeFile('test-summary.js');
        assert.ok(output.includes('Summary for test-summary.js'), `Output: ${output}`);
        assert.ok(output.includes('Total Lines: 13'));
        assert.ok(output.includes('- Imports/Requires: 2'));
        assert.ok(output.includes('- Classes: 1'));
        assert.ok(output.includes('- Functions/Methods: 2')); // myMethod and globalFunc
    });

    it('should return error if file not found', async () => {
        const output = await summarizeFile('unknown-file.js');
        assert.ok(output.includes('Error: File not found'));
    });

    it('should return error for missing parameters', async () => {
        const output = await summarizeFile('');
        assert.strictEqual(output, 'Error: Missing filePath parameter.');
    });
});
