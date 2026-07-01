const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const searchDesignDocs = require('../searchDesignDocs.js');

describe('searchDesignDocs Tool', () => {
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
        const output = await searchDesignDocs('Command');
        assert.ok(output.includes('=== Design Documents Search Results'), 'Should contain header');
        assert.ok(output.includes('ARCH-001'), 'Should match ARCH-001');
        assert.ok(output.includes('Extension Command Architecture'), 'Should include title');
    });

    it('should search using the custom workspace file if present', async () => {
        const customDb = {
            designDocs: [
                {
                    id: "ARCH-999",
                    title: "Custom Workspace Architecture Doc",
                    content: "Architecture context content"
                }
            ]
        };

        fs.writeFileSync(customKbPath, JSON.stringify(customDb, null, 2));
        customFileCreated = true;

        const output = await searchDesignDocs('Custom');
        assert.ok(output.includes('ARCH-999'), 'Should match custom ARCH-999');
        assert.ok(output.includes('Custom Workspace Architecture Doc'), 'Should include custom title');
        
        const defaultMatch = await searchDesignDocs('Command');
        assert.ok(defaultMatch.includes('No design documents found matching'), 'Should not find default doc');
    });

    it('should return error for empty query', async () => {
        const output = await searchDesignDocs('');
        assert.strictEqual(output, 'Error: No query provided.');
    });

    it('should handle no matches gracefully', async () => {
        const output = await searchDesignDocs('NonExistentDocABC123');
        assert.strictEqual(output, 'No design documents found matching: NonExistentDocABC123');
    });
});
