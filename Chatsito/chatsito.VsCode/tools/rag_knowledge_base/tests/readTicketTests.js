const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const readTicket = require('../readTicket.js');

describe('readTicket Tool', () => {
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
        const output = await readTicket('TASK-101');
        assert.ok(output.includes('=== Ticket: Fix memory leak in extension host (TASK-101) ==='), 'Should contain header');
        assert.ok(output.includes('Status: In Progress'), 'Should contain status');
        assert.ok(output.includes('Alice Smith'), 'Should contain assignee');
        assert.ok(output.includes('Comments:'), 'Should contain comments section');
    });

    it('should read items from custom workspace file if present', async () => {
        const customDb = {
            tickets: [
                {
                    id: "TASK-999",
                    title: "Custom Workspace Ticket",
                    description: "Custom description text",
                    status: "Completed",
                    assignee: "Tester",
                    labels: ["test"],
                    comments: [],
                    linkedItems: []
                }
            ]
        };

        fs.writeFileSync(customKbPath, JSON.stringify(customDb, null, 2));
        customFileCreated = true;

        const output = await readTicket('TASK-999');
        assert.ok(output.includes('=== Ticket: Custom Workspace Ticket (TASK-999) ==='), 'Should contain custom header');
        assert.ok(output.includes('Custom description text'), 'Should contain custom description');
    });

    it('should return error for empty ticket ID', async () => {
        const output = await readTicket('');
        assert.strictEqual(output, 'Error: No ticket ID provided.');
    });

    it('should return error when ticket is not found', async () => {
        const output = await readTicket('TASK-NOTFOUND');
        assert.strictEqual(output, 'Error: Ticket not found with ID: TASK-NOTFOUND');
    });
});
