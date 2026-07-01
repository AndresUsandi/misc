const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const readPullRequest = require('../readPullRequest.js');

describe('readPullRequest Tool', () => {
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
        const output = await readPullRequest('PR-201');
        assert.ok(output.includes('=== Pull Request: Fix memory leaks from registered event listeners (PR-201) ==='), 'Should contain header');
        assert.ok(output.includes('Status: Open'), 'Should contain status');
        assert.ok(output.includes('Author: Alice Smith'), 'Should contain author');
        assert.ok(output.includes('Reviews:'), 'Should contain reviews section');
    });

    it('should read items from custom workspace file if present', async () => {
        const customDb = {
            pullRequests: [
                {
                    id: "PR-999",
                    title: "Custom Workspace PR",
                    author: "Tester",
                    description: "Custom description text",
                    status: "Merged",
                    changedFiles: ["app.js"],
                    reviews: [],
                    statusChecks: "Passed"
                }
            ]
        };

        fs.writeFileSync(customKbPath, JSON.stringify(customDb, null, 2));
        customFileCreated = true;

        const output = await readPullRequest('PR-999');
        assert.ok(output.includes('=== Pull Request: Custom Workspace PR (PR-999) ==='), 'Should contain custom header');
        assert.ok(output.includes('Custom description text'), 'Should contain custom description');
    });

    it('should return error for empty PR ID', async () => {
        const output = await readPullRequest('');
        assert.strictEqual(output, 'Error: No PR ID provided.');
    });

    it('should return error when PR is not found', async () => {
        const output = await readPullRequest('PR-NOTFOUND');
        assert.strictEqual(output, 'Error: Pull request not found with ID: PR-NOTFOUND');
    });
});
