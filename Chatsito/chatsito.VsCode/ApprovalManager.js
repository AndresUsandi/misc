const vscode = require('vscode');
const path = require('path');
const logger = require('./logger');

class ApprovalManager {
    /**
     * Determines whether the requested tool execution needs user approval.
     */
    async requestApproval(toolName, args, selectedMode) {
        // AI-Mode auto-approves everything
        if (selectedMode === 'ai') {
            return true;
        }

        const ToolDefinitionProvider = require('./ToolDefinitionProvider');
        const toolDef = ToolDefinitionProvider.getToolDefinition(toolName);
        const isDestructive = toolDef ? toolDef.isDestructive : false;

        // Non-destructive tools (e.g. view file, search) are always auto-approved UNLESS in user mode
        if (!isDestructive && selectedMode !== 'user') {
            return true;
        }


        // Needs user approval (User mode, or Hybrid mode outside workspace / command exec)
        return await this.showApprovalPrompt(toolName, args);
    }

    async showApprovalPrompt(toolName, args) {
        let message = `Chatsito wants to execute: ${toolName}\n\n`;
        message += `Arguments:\n${logger.formatJson(args)}`;
        
        const selection = await vscode.window.showWarningMessage(
            message,
            { modal: true },
            'Approve',
            'Reject'
        );

        const isApproved = selection === 'Approve';
        logger.log(`[ApprovalManager] User ${isApproved ? 'approved' : 'rejected'} execution of ${toolName}`);
        return isApproved;
    }
}

module.exports = new ApprovalManager();
