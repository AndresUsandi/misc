const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const readKnowledgeItem = require('../readKnowledgeItem.js');

describe('readKnowledgeItem Tool', () => {
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

    it('should read items from default built-in database when no custom file is present', async () => {
        const output = await readKnowledgeItem('KB-001');
        assert.ok(output.includes('=== Knowledge Item: Onboarding Guide (KB-001) ==='), 'Should contain header');
        assert.ok(output.includes('Welcome to Chatsito!'), 'Should contain content snippet');
    });

    it('should read items from custom workspace file if present', async () => {
        const customDb = {
            knowledgeItems: [
                {
                    id: "KB-999",
                    title: "Custom Project Guide",
                    content: "Custom content test",
                    tags: ["custom"]
                }
            ]
        };

        fs.writeFileSync(customKbPath, JSON.stringify(customDb, null, 2));
        customFileCreated = true;

        const output = await readKnowledgeItem('KB-999');
        assert.ok(output.includes('=== Knowledge Item: Custom Project Guide (KB-999) ==='), 'Should contain custom header');
        assert.ok(output.includes('Custom content test'), 'Should contain custom content');
    });

    it('should return error for empty item ID', async () => {
        const output = await readKnowledgeItem('');
        assert.strictEqual(output, 'Error: No item ID provided.');
    });

    it('should return error when item is not found', async () => {
        const output = await readKnowledgeItem('KB-NOTFOUND');
        assert.strictEqual(output, 'Error: Knowledge item not found with ID: KB-NOTFOUND');
    });
});
