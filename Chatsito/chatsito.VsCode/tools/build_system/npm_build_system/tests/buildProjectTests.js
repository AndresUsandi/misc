const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildProject = require('../buildProject.js');

describe('buildProject Tool', function () {
    this.timeout(20000);

    it('should successfully build the project', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_build');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        // Setup mock package.json with a build script
        const pkgPath = path.join(testDir, 'package.json');
        const pkgData = {
            name: "mock-build-proj",
            scripts: { "build": "node -e \"console.log('MOCK BUILD SUCCESS')\"" }
        };
        fs.writeFileSync(pkgPath, JSON.stringify(pkgData), 'utf8');
        
        const output = await buildProject(testDir);
        
        assert.ok(output.includes('Build Results'), `Output: ${output}`);
        assert.ok(output.includes('MOCK BUILD SUCCESS'), 'Should capture stdout of build command');
        assert.ok(output.includes('Build succeeded'), 'Should report success');
        
        fs.unlinkSync(pkgPath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await buildProject('');
        assert.strictEqual(output, 'Error: Missing projectPath parameter.');
    });
});
