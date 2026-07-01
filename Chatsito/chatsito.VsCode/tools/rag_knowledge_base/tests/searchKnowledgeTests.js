const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const searchKnowledge = require('../searchKnowledge.js');

describe('searchKnowledge Tool', () => {
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
        const output = await searchKnowledge('Onboarding');
        assert.ok(output.includes('=== Knowledge Base Search Results'), 'Should contain header');
        assert.ok(output.includes('KB-001'), 'Should match onboarding guide KB-001');
        assert.ok(output.includes('Onboarding Guide'), 'Should include title');
    });

    it('should search using the custom workspace file if present', async () => {
        const customDb = {
            knowledgeItems: [
                {
                    id: "KB-999",
                    title: "Custom Project Guide",
                    content: "This is a custom guide stored in workspace files.",
                    tags: ["custom", "test"]
                }
            ]
        };

        fs.writeFileSync(customKbPath, JSON.stringify(customDb, null, 2));
        customFileCreated = true;

        const output = await searchKnowledge('Custom');
        assert.ok(output.includes('KB-999'), 'Should match custom KB-999');
        assert.ok(output.includes('Custom Project Guide'), 'Should include custom title');
        
        const defaultMatch = await searchKnowledge('Onboarding');
        assert.ok(defaultMatch.includes('No knowledge items found matching'), 'Should not find default guide');
    });

    it('should return error for empty query', async () => {
        const output = await searchKnowledge('');
        assert.strictEqual(output, 'Error: No query provided.');
    });

    it('should handle no matches gracefully', async () => {
        const output = await searchKnowledge('NonExistentTermABC123');
        assert.strictEqual(output, 'No knowledge items found matching: NonExistentTermABC123');
    });
});
