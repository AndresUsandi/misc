const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const searchTickets = require('../searchTickets.js');

describe('searchTickets Tool', () => {
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
        const output = await searchTickets('TASK-101');
        assert.ok(output.includes('=== Ticket Search Results'), 'Should contain header');
        assert.ok(output.includes('TASK-101'), 'Should match task TASK-101');
        assert.ok(output.includes('Fix memory leak'), 'Should include title');
    });

    it('should search using the custom workspace file if present', async () => {
        const customDb = {
            tickets: [
                {
                    id: "TASK-999",
                    title: "Custom Workspace Ticket",
                    description: "Custom description",
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

        const output = await searchTickets('Custom');
        assert.ok(output.includes('TASK-999'), 'Should match custom TASK-999');
        assert.ok(output.includes('Custom Workspace Ticket'), 'Should include custom title');
        
        const defaultMatch = await searchTickets('TASK-101');
        assert.ok(defaultMatch.includes('No tickets found matching'), 'Should not find default ticket');
    });

    it('should return error for empty query', async () => {
        const output = await searchTickets('');
        assert.strictEqual(output, 'Error: No query provided.');
    });

    it('should handle no matches gracefully', async () => {
        const output = await searchTickets('NonExistentTicketABC123');
        assert.strictEqual(output, 'No tickets found matching: NonExistentTicketABC123');
    });
});
