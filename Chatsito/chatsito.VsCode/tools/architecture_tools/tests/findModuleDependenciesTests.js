const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const findModuleDependencies = require('../findModuleDependencies.js');

describe('findModuleDependencies Tool', function () {
    this.timeout(20000);

    it('should parse JS/TS imports and exports', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_modules');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const filePath = path.join(testDir, 'main.js');
        const fileContent = `
            const fs = require('fs');
            import path from 'path';
            import { myFunc } from './utils.js';
            export { default as stuff } from './stuff.js';
        `;
        fs.writeFileSync(filePath, fileContent, 'utf8');
        
        const output = await findModuleDependencies(filePath);
        
        assert.ok(output.includes('fs'), 'Should find fs');
        assert.ok(output.includes('path'), 'Should find path');
        assert.ok(output.includes('./utils.js'), 'Should find utils.js');
        assert.ok(output.includes('./stuff.js'), 'Should find stuff.js');
        
        fs.unlinkSync(filePath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await findModuleDependencies('');
        assert.strictEqual(output, 'Error: Missing filePath parameter.');
    });
});
