const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const getCodeCoverage = require('../getCodeCoverage.js');

describe('getCodeCoverage Tool', function () {
    this.timeout(20000);

    it('should successfully get code coverage', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_coverage');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const scriptPath = path.join(testDir, 'script.js');
        fs.writeFileSync(scriptPath, "console.log('MOCK COVERAGE 100%');", 'utf8');

        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-coverage",
            scripts: { "test": "node script.js" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await getCodeCoverage(testDir);
        
        assert.ok(output.includes('Code Coverage Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK COVERAGE 100%'), 'Should capture stdout');
        assert.ok(output.includes('Coverage gathered successfully'), 'Should report success');
        
        fs.unlinkSync(pkgPath);
        fs.unlinkSync(scriptPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await getCodeCoverage('');
        assert.strictEqual(output, 'Error: Missing projectPath parameter.');
    });
});
