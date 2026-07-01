const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const searchPullRequests = require('../searchPullRequests.js');

describe('searchPullRequests Tool', () => {
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
        const output = await searchPullRequests('PR-201');
        assert.ok(output.includes('=== Pull Request Search Results'), 'Should contain header');
        assert.ok(output.includes('PR-201'), 'Should match PR PR-201');
        assert.ok(output.includes('Fix memory leaks'), 'Should include title');
    });

    it('should search using the custom workspace file if present', async () => {
        const customDb = {
            pullRequests: [
                {
                    id: "PR-999",
                    title: "Custom Workspace PR",
                    author: "Tester",
                    description: "Custom description",
                    status: "Merged",
                    changedFiles: ["app.js"],
                    reviews: [],
                    statusChecks: "Passed"
                }
            ]
        };

        fs.writeFileSync(customKbPath, JSON.stringify(customDb, null, 2));
        customFileCreated = true;

        const output = await searchPullRequests('Custom');
        assert.ok(output.includes('PR-999'), 'Should match custom PR-999');
        assert.ok(output.includes('Custom Workspace PR'), 'Should include custom title');
        
        const defaultMatch = await searchPullRequests('PR-201');
        assert.ok(defaultMatch.includes('No pull requests found matching'), 'Should not find default PR');
    });

    it('should return error for empty query', async () => {
        const output = await searchPullRequests('');
        assert.strictEqual(output, 'Error: No query provided.');
    });

    it('should handle no matches gracefully', async () => {
        const output = await searchPullRequests('NonExistentPRABC123');
        assert.strictEqual(output, 'No pull requests found matching: NonExistentPRABC123');
    });
});
