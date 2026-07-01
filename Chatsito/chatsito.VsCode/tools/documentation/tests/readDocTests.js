const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const readDoc = require('../readDoc.js');

describe('readDoc Tool', function () {
    this.timeout(10000);

    let testDir;
    let docsDir;
    let docPath1;
    let docPath2;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        testDir = workspaceFolders[0].uri.fsPath;
        docsDir = path.join(testDir, 'docs');
        
        if (!fs.existsSync(docsDir)) fs.mkdirSync(docsDir, { recursive: true });

        docPath1 = path.join(testDir, 'README.md');
        docPath2 = path.join(docsDir, 'architecture.md');

        fs.writeFileSync(docPath1, '# Project README\nHello world!');
        fs.writeFileSync(docPath2, '# Architecture\nDesign goes here.');
    });

    after(() => {
        if (fs.existsSync(docPath1)) fs.unlinkSync(docPath1);
        if (fs.existsSync(docPath2)) fs.unlinkSync(docPath2);
        if (fs.existsSync(docsDir)) fs.rmdirSync(docsDir);
    });

    it('should successfully read a markdown file in root', async () => {
        const output = await readDoc('README.md');
        assert.ok(output.includes('Documentation: README.md'), `Output: ${output}`);
        assert.ok(output.includes('# Project README'));
    });

    it('should successfully read a markdown file in docs/ directory', async () => {
        const output = await readDoc('architecture'); // without .md
        assert.ok(output.includes('Documentation: docs\\architecture.md') || output.includes('Documentation: docs/architecture.md'), `Output: ${output}`);
        assert.ok(output.includes('# Architecture'));
    });

    it('should return error if file not found', async () => {
        const output = await readDoc('unknown-doc');
        assert.ok(output.includes('Error: Documentation file not found'));
    });

    it('should return error for missing parameters', async () => {
        const output = await readDoc('');
        assert.strictEqual(output, 'Error: Missing filePath parameter.');
    });
});
