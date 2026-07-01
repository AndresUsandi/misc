const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const searchDecisions = require('../searchDecisions.js');

describe('searchDecisions Tool', () => {
    const workspaceRoot = vscode.workspace.workspaceFolders[0].uri.fsPath;
    const chatsitoDir = path.resolve(workspaceRoot, '.chatsito');
    const customKbPath = path.resolve(chatsitoDir, 'knowledge_base.json');
    let customFileCreated = false;

    beforeEach(() => {
        if (!fs.existsSync(chatsitoDir)) {
            fs.mkdirSync(chatsitoDir, { recursive: true });
        }
    });

    afterEach(() => {
        if (customFileCreated && fs.existsSync(customKbPath)) {
            fs.unlinkSync(customKbPath);
            customFileCreated = false;
        }
    });

    it('should search using the default built-in database when no custom file is present', async () => {
        const output = await searchDecisions('Local JSON');
        assert.ok(output.includes('=== Architecture Decisions (ADR) Search Results'), 'Should contain header');
        assert.ok(output.includes('ADR-001'), 'Should match ADR-001');
        assert.ok(output.includes('Use Local JSON Mocks'), 'Should include title');
    });

    it('should search using the custom workspace file if present', async () => {
        const customDb = {
            decisions: [
                {
                    id: "ADR-999",
                    title: "Custom Workspace ADR",
                    content: "ADR context content"
                }
            ]
        };

        fs.writeFileSync(customKbPath, JSON.stringify(customDb, null, 2));
        customFileCreated = true;

        const output = await searchDecisions('Custom');
        assert.ok(output.includes('ADR-999'), 'Should match custom ADR-999');
        assert.ok(output.includes('Custom Workspace ADR'), 'Should include custom title');
        
        const defaultMatch = await searchDecisions('Local JSON');
        assert.ok(defaultMatch.includes('No architecture decisions found matching'), 'Should not find default ADR');
    });

    it('should return error for empty query', async () => {
        const output = await searchDecisions('');
        assert.strictEqual(output, 'Error: No query provided.');
    });

    it('should handle no matches gracefully', async () => {
        const output = await searchDecisions('NonExistentADRABC123');
        assert.strictEqual(output, 'No architecture decisions found matching: NonExistentADRABC123');
    });
});
