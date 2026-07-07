import readline from 'readline';
import path from 'path';
import { logger } from './logger.js';
import ToolDefinitionProvider from './ToolDefinitionProvider.js';

class ApprovalManager {
    /**
     * Determines whether the requested tool execution needs user approval.
     */
    async requestApproval(toolName, args, selectedMode) {
        if (selectedMode === 'ai') {
            return true;
        }

        const toolDef = ToolDefinitionProvider.getToolDefinition(toolName);
        const isDestructive = toolDef ? toolDef.isDestructive : false;

        if (!isDestructive && selectedMode !== 'user') {
            return true;
        }

        if (selectedMode === 'hybrid') {
            let targetsWorkspace = false;
            const targetPath = args?.filePath || args?.uri || args?.projectPath || args?.solutionPath;
            if (targetPath) {
                try {
                    const absolutePath = path.resolve(targetPath);
                    const root = path.resolve(process.cwd());
                    if (absolutePath.startsWith(root)) {
                        targetsWorkspace = true;
                    }
                } catch (e) {
                    // ignore
                }
            } else {
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

        return await this.showApprovalPrompt(toolName, args);
    }

    async showApprovalPrompt(toolName, args) {
        let message = `\n[APPROVAL REQUEST] Chatsito wants to execute: ${toolName}\n`;
        message += `Arguments:\n${logger.formatJson ? logger.formatJson(args) : JSON.stringify(args, null, 2)}\n`;
        console.log(message);

        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        return new Promise(resolve => {
            rl.question('Approve this execution? (y/N): ', (answer) => {
                rl.close();
                const isApproved = answer.trim().toLowerCase() === 'y' || answer.trim().toLowerCase() === 'yes';
                logger.log(`[ApprovalManager] User ${isApproved ? 'approved' : 'rejected'} execution of ${toolName}`);
                resolve(isApproved);
            });
        });
    }
}

export default new ApprovalManager();
