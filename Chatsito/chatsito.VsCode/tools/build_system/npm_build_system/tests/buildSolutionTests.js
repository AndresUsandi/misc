const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildSolution = require('../buildSolution.js');

describe('buildSolution Tool', function () {
    this.timeout(20000);

    it('should successfully build the solution', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_solution');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-sol",
            scripts: { "build": "node -e \"console.log('MOCK SOLUTION SUCCESS')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await buildSolution(testDir);
        
        assert.ok(output.includes('Solution Build Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK SOLUTION SUCCESS'), 'Should capture stdout');
        assert.ok(output.includes('Solution build succeeded'), 'Should report success');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await buildSolution('');
        assert.strictEqual(output, 'Error: Missing solutionPath parameter.');
    });
});
