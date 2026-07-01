const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const getProjectDependencies = require('../getProjectDependencies.js');

describe('getProjectDependencies Tool', function () {
    this.timeout(20000);

    it('should parse package.json and list dependencies', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_project');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-proj",
            dependencies: { "mocha": "10.0.0" },
            devDependencies: { "chai": "4.0.0" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await getProjectDependencies(testDir);
        
        assert.ok(output.includes('Dependencies for mock-proj'), `Output: ${output}`);
        assert.ok(output.includes('mocha: 10.0.0'));
        assert.ok(output.includes('chai: 4.0.0'));
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await getProjectDependencies('');
        assert.strictEqual(output, 'Error: Missing projectPath parameter.');
    });
});
