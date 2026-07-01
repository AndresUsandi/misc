const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const getFullGraph = require('../getFullGraph.js');

describe('getFullGraph Tool', function () {
    this.timeout(20000);

    it('should generate a full backwards call graph', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const testDir = path.join(root, 'test', 'fixtures', 'mock_graph');
        
        if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
        
        const filePath = path.join(testDir, 'main.js');
        // A simple JS file that has a caller and callee
        const fileContent = `
function callee() {
    return 1;
}
function caller() {
    return callee();
}
caller();
`;
        fs.writeFileSync(filePath, fileContent, 'utf8');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(filePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Find graph for "callee" at line 1, char 12
        const output = await getFullGraph(filePath, 1, 12);
        
        assert.ok(output.includes('full backwards call graph'), `Output: ${output}`);
        assert.ok(output.includes('callee'), 'Should include callee');
        assert.ok(output.includes('caller'), 'Should include caller in graph');
        
        fs.unlinkSync(filePath);
        fs.rmdirSync(testDir);
    });

    it('should return error for missing parameters', async () => {
        const output = await getFullGraph('', 0, 0);
        assert.strictEqual(output, 'Error: No file path provided.');
    });
});
