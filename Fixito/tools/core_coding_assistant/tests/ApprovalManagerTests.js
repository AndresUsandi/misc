const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const ApprovalManager = require('../../../ApprovalManager');
const ToolManager = require('../../../ToolManager');

describe('ApprovalManager Tests', function () {
    let originalShowWarningMessage;
    let mockUserSelection = 'Approve';

    before(() => {
        originalShowWarningMessage = vscode.window.showWarningMessage;
        vscode.window.showWarningMessage = async (msg, options, ...items) => {
            return mockUserSelection;
        };
    });

    after(() => {
        vscode.window.showWarningMessage = originalShowWarningMessage;
    });

    beforeEach(() => {
        mockUserSelection = 'Approve';
    });

    it('should auto-approve in ai mode', async () => {
        const result = await ApprovalManager.requestApproval('runCommand', { command: 'echo 1' }, 'ai');
        assert.strictEqual(result, true, 'AI mode should always approve');
    });

    it('should prompt in user mode even for non-destructive tools', async () => {
        mockUserSelection = 'Reject';
        const result = await ApprovalManager.requestApproval('readFile', { filePath: 'test.js' }, 'user');
        assert.strictEqual(result, false, 'User mode should prompt and can reject');
    });

    it('should auto-approve non-destructive tools in hybrid mode', async () => {
        mockUserSelection = 'Reject'; // Should not even prompt
        const result = await ApprovalManager.requestApproval('readFile', { filePath: 'test.js' }, 'hybrid');
        assert.strictEqual(result, true, 'Hybrid mode should auto-approve non-destructive tools');
    });

    it('should prompt for command execution in hybrid mode', async () => {
        mockUserSelection = 'Approve';
        const result = await ApprovalManager.requestApproval('runCommand', { command: 'echo 1' }, 'hybrid');
        assert.strictEqual(result, true, 'Should approve if user clicks Approve');

        mockUserSelection = 'Reject';
        const result2 = await ApprovalManager.requestApproval('runCommand', { command: 'echo 1' }, 'hybrid');
        assert.strictEqual(result2, false, 'Should reject if user clicks Reject');
    });

    it('should properly detect workspace boundaries in hybrid mode', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            this.skip();
        }
        const workspaceRoot = workspaceFolders[0].uri.fsPath;

        // Inside workspace
        const insidePath = path.join(workspaceRoot, 'test.js');
        let result = await ApprovalManager.requestApproval('insertCode', { filePath: insidePath }, 'hybrid');
        assert.strictEqual(result, true, 'Should auto-approve inside workspace');

        // Outside workspace
        const outsidePath = path.join(path.dirname(workspaceRoot), 'outside.js');
        mockUserSelection = 'Reject';
        result = await ApprovalManager.requestApproval('insertCode', { filePath: outsidePath }, 'hybrid');
        assert.strictEqual(result, false, 'Should prompt for outside workspace');
    });

    it('ResponseRouter should respect ApprovalManager result', async () => {
        const ResponseRouter = require('../../../ResponseRouter');
        const toolManager = new ToolManager();
        const mockClient = { sendProgress: () => { } };

        mockUserSelection = 'Reject';
        const msg = {
            tool_calls: [{
                function: { name: 'runCommand', arguments: { command: 'echo 1' } }
            }]
        };

        const result = await ResponseRouter.routeToolCall(msg.tool_calls[0], mockClient, toolManager, 'hybrid');
        assert.strictEqual(result.action, 'tool_executed');
        assert.ok(result.toolResult.includes('Execution cancelled'), 'Should return cancellation message');
    });
});
