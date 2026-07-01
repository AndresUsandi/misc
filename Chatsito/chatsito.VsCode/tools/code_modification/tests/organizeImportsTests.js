const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const organizeImports = require('../organizeImports.js');

describe('organizeImports Tool', function () {
    this.timeout(20000);

    it('should attempt to organize imports', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'OrganizeFixture.js');
        
        fs.writeFileSync(fixturePath, 'const path = require("path");\nconst fs = require("fs");\nconsole.log(fs, path);\n', 'utf8');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const output = await organizeImports(fixturePath);
        
        assert.ok(output.includes('Successfully organized') || output.includes('Executed organize imports') || output.includes('No organize imports provider'), `Output: ${output}`);
        
        fs.unlinkSync(fixturePath);
    });

    it('should return error for missing parameters', async () => {
        const output = await organizeImports('');
        assert.strictEqual(output, 'Error: Missing required parameters.');
    });
});
