const vscode = require('vscode');
const path = require('path');
const logger = require('./logger');

class ApprovalManager {
    /**
     * Determines whether the requested tool execution needs user approval.
     */
    async requestApproval(toolName, args, selectedMode) {
        const ToolDefinitionProvider = require('./ToolDefinitionProvider');
        const toolDef = ToolDefinitionProvider.getToolDefinition(toolName);
        const isDestructive = toolDef ? toolDef.isDestructive : false;
        const isAdminTool = toolDef ? toolDef.isAdminTool : false;

        // Admin-Mode auto-approves everything
        if (selectedMode === 'admin') {
            return true;
        }

        // AI-Mode auto-approves everything EXCEPT Admin Tools (like runCommand)
        if (selectedMode === 'ai' && !isAdminTool) {
            return true;
        }

        // Non-destructive tools (e.g. view file, search) are always auto-approved UNLESS in user mode
        if (!isDestructive && selectedMode !== 'user') {
            return true;
        }

        // If in hybrid mode, check if the tool targets a workspace file
        if (selectedMode === 'hybrid') {
            let targetsWorkspace = false;
            const targetPath = args?.filePath || args?.uri || args?.projectPath || args?.solutionPath;
            if (targetPath) {
                try {
                    const PathResolver = require('./PathResolver');
                    const absolutePath = PathResolver.resolveAndValidateWorkspacePath(targetPath);
                    const uri = vscode.Uri.file(absolutePath);
                    if (vscode.workspace.getWorkspaceFolder(uri) !== undefined) {
                        targetsWorkspace = true;
                    }
                } catch (e) {
                    // ignore
                }
            } else {
                // If no path argument is provided, check if the tool schema accepts a path parameter.
                // If it does, we assume it defaults to the workspace root.
                const properties = toolDef?.schema?.parameters?.properties;
                const hasPathParameter = properties && Object.keys(properties).some(key =>
                    ['projectPath', 'solutionPath', 'filePath', 'uri'].includes(key)
                );
                if (hasPathParameter) {
                    targetsWorkspace = true;
                }
            }
            if (targetsWorkspace) {
                return true;
            }
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
