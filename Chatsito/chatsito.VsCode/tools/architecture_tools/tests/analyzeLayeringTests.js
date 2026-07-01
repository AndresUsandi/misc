const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const analyzeLayering = require('../analyzeLayering.js');

describe('analyzeLayering Tool', function () {
    this.timeout(20000);

    it('should detect layering violations', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_layers');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const controllersDir = path.join(testDir, 'controllers');
        const servicesDir = path.join(testDir, 'services');
        fs.mkdirSync(controllersDir);
        fs.mkdirSync(servicesDir);
        
        // Controller imports service (allowed)
        fs.writeFileSync(path.join(controllersDir, 'ctrl.js'), 'const svc = require("../services/svc.js");', 'utf8');
        // Service imports controller (violation)
        fs.writeFileSync(path.join(servicesDir, 'svc.js'), 'const ctrl = require("../controllers/ctrl.js");', 'utf8');
        
        const rules = {
            "controllers": ["services"],
            "services": [] // Services cannot import controllers
        };
        
        const output = await analyzeLayering(testDir, JSON.stringify(rules));
        
        assert.ok(output.includes('Layering Violations Found'), `Output: ${output}`);
        assert.ok(output.includes('illegally imports ../controllers/ctrl.js'), 'Should flag the illegal import');
        
        fs.unlinkSync(path.join(controllersDir, 'ctrl.js'));
        fs.unlinkSync(path.join(servicesDir, 'svc.js'));
        fs.rmdirSync(controllersDir);
        fs.rmdirSync(servicesDir);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await analyzeLayering('', '');
        assert.strictEqual(output, 'Error: Missing directory parameter.');
    });
});
