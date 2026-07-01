const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const searchDocs = require('../searchDocs.js');

describe('searchDocs Tool', function () {
    this.timeout(10000);

    let testDir;
    let docPath;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        testDir = path.join(workspaceFolders[0].uri.fsPath, 'test-docs');
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });

        docPath = path.join(testDir, 'api.md');
        fs.writeFileSync(docPath, '# API\nThis is a super-secret API.\n');
    });

    after(() => {
        if (fs.existsSync(docPath)) fs.unlinkSync(docPath);
        if (fs.existsSync(testDir)) fs.rmdirSync(testDir);
    });

    it('should successfully search and find matching lines in markdown files', async () => {
        // FindFiles needs time to index the newly created files sometimes
        await new Promise(r => setTimeout(r, 1000));
        
        const output = await searchDocs('super-secret');
        assert.ok(output.includes('Documentation Search Results for "super-secret"'), `Output: ${output}`);
        assert.ok(output.includes('This is a super-secret API.'));
        assert.ok(output.includes('Total matches: 1'));
    });

    it('should return no matches if query not found', async () => {
        const output = await searchDocs('NotPresentInDocs');
        assert.ok(output.includes('No matches found for "NotPresentInDocs"'), `Output: ${output}`);
    });

    it('should return error for missing parameters', async () => {
        const output = await searchDocs('');
        assert.strictEqual(output, 'Error: Missing query parameter.');
    });
});
