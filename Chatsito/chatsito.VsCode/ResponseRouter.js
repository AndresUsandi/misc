const logger = require('./logger');
const ToolDefinitionProvider = require('./ToolDefinitionProvider');
const ApprovalManager = require('./ApprovalManager');
const PatchManager = require('./PatchManager');

class ResponseRouter {
    /**
     * Routes a single tool call to the appropriate execution path.
     * @param {Object} toolCall - The tool call object.
     * @param {Object} webviewClient - The client for sending UI updates.
     * @param {Object} toolManager - The instance of ToolManager.
     * @param {string} selectedMode - The current security mode.
     * @returns {Object} An object describing the action taken.
     */
    static async routeToolCall(toolCall, webviewClient, toolManager, selectedMode) {
        if (toolCall && toolCall.function) {
                const toolName = toolCall.function.name;
                const args = toolCall.function.arguments || {};

                const def = ToolDefinitionProvider.getToolDefinition(toolName);
                if (!def) {
                    return {
                        action: 'tool_executed',
                        toolName: toolName,
                        toolResult: `Error: Unknown tool '${toolName}'.`
                    };
                }

                // 1. Get Progress Text dynamically
                const progressText = def.getProgressText ? def.getProgressText(args) : `Executing tool ${toolName}...`;
                webviewClient.sendProgress(progressText);
                logger.log(`[ResponseRouter] Routing tool ${toolName} with args: ${logger.formatJson(args)}`);

                // 2. Request Approval if necessary
                if (def.isDestructive && !def.isPatchingTool) {
                    // ApprovalManager checks security mode (User, Hybrid, AI) natively.
                    const isApproved = await ApprovalManager.requestApproval(toolName, args, selectedMode);
                    if (!isApproved) {
                        return {
                            action: 'tool_executed',
                            toolName: toolName,
                            toolResult: `Execution cancelled: User denied permission to run ${toolName}.`
                        };
                    }
                }

                // 3. Execute Tool
                let toolResult;
                try {
                    if (def.isPatchingTool) {
                        toolResult = await PatchManager.executeTool(toolName, args, selectedMode);
                    } else {
                        toolResult = await toolManager.executeTool(toolName, args);
                    }
                } catch (err) {
                    logger.log(`[ResponseRouter] Error executing tool ${toolName}: ${err.message}`);
                    toolResult = `Error: ${err.message}`;
                }

                let resultString = typeof toolResult === 'string' ? toolResult : logger.formatJson(toolResult);
                if (resultString && resultString.length > 3000) {
                    logger.log(`[ResponseRouter] Tool ${toolName} completed. Result: ${resultString.substring(0, 3000)}... (truncated)`);
                } else {
                    logger.log(`[ResponseRouter] Tool ${toolName} completed. Result: ${resultString}`);
                }

                return {
                    action: 'tool_executed',
                    toolName: toolName,
                    toolResult: toolResult
                };
            }
        return {
            action: 'final_answer'
        };
    }
}

module.exports = ResponseRouter;
