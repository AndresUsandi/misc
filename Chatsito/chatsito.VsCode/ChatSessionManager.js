const vscode = require('vscode');
const logger = require('./logger');
const ChatsitoApiClient = require('./ChatsitoApiClient');
const ToolManager = require('./ToolManager');
const ResponseRouter = require('./ResponseRouter');

const getInitialPromptContext = require('./ContextBuilder');

class ChatSessionManager {
    constructor(context) {
        this.context = context; // ExtensionContext
        this.conversationHistory = [];
        this.currentRequest = null;
        this.activeWorkspace = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath || '';
        this._selectedMode = (this.context && this.context.globalState)
            ? (this.context.globalState.get('chatsito.selectedMode') || 'hybrid')
            : 'hybrid';
        this.pendingToolResults = {};
        this.pendingApprovals = [];
        this.previousPrompts = [];
        this.contextTokenSize = 16384;
        this.savedSessionMetadata = [];
        this.chatsitoApiClient = new ChatsitoApiClient();
        this.toolManager = new ToolManager();

        this.loadSavedSessionMetadata();
        this.initializeApiClient();
    }

    async initializeApiClient() {
        await this.chatsitoApiClient.initialize();
        if (this.context && this.context.globalState) {
            const savedModel = this.context.globalState.get('chatsito.activeModel');
            if (savedModel && this.availableModels.includes(savedModel)) {
                this.activeModel = savedModel;
            }
        }
        if (this.webviewClient) {
            this.webviewClient.sendStateUpdate();
        }
    }

    get selectedMode() {
        return this._selectedMode;
    }

    set selectedMode(value) {
        this._selectedMode = value;
        if (this.context && this.context.globalState) {
            this.context.globalState.update('chatsito.selectedMode', value);
        }
    }

    get activeModel() {
        return this.chatsitoApiClient.activeModel;
    }

    set activeModel(value) {
        this.chatsitoApiClient.activeModel = value;
        if (this.context && this.context.globalState) {
            this.context.globalState.update('chatsito.activeModel', value);
        }
    }

    get availableModels() {
        return this.chatsitoApiClient.availableModels;
    }

    set availableModels(value) {
        this.chatsitoApiClient.availableModels = value;
    }

    loadSavedSessionMetadata() {
        if (!this.context) return;
        const sessions = this.context.workspaceState.get('chatsito.saved_sessions') || [];
        this.savedSessionMetadata = sessions.map(s => ({
            id: s.id,
            name: s.name,
            timestamp: s.timestamp,
            historyLength: s.conversationHistory.length
        }));
    }

    async saveSession(name) {
        if (!this.context) return;
        const sessions = this.context.workspaceState.get('chatsito.saved_sessions') || [];
        const sessionId = 'session_' + Date.now();
        const newSession = {
            id: sessionId,
            name: name || `Session ${new Date().toLocaleString()}`,
            timestamp: Date.now(),
            conversationHistory: this.conversationHistory,
            contextTokenSize: this.contextTokenSize,
            activeModel: this.activeModel,
            selectedMode: this.selectedMode,
            previousPrompts: this.previousPrompts
        };
        sessions.push(newSession);
        await this.context.workspaceState.update('chatsito.saved_sessions', sessions);
        this.loadSavedSessionMetadata();
        return sessionId;
    }

    async restoreSession(sessionId) {
        if (!this.context) return false;
        const sessions = this.context.workspaceState.get('chatsito.saved_sessions') || [];
        const session = sessions.find(s => s.id === sessionId);
        if (session) {
            this.conversationHistory = session.conversationHistory || [];
            this.contextTokenSize = session.contextTokenSize || 16384;
            this.activeModel = session.activeModel || '';
            this.selectedMode = session.selectedMode || 'hybrid';
            this.previousPrompts = session.previousPrompts || [];
            return true;
        }
        return false;
    }

    async deleteSavedSession(sessionId) {
        if (!this.context) return;
        let sessions = this.context.workspaceState.get('chatsito.saved_sessions') || [];
        sessions = sessions.filter(s => s.id !== sessionId);
        await this.context.workspaceState.update('chatsito.saved_sessions', sessions);
        this.loadSavedSessionMetadata();
    }

    startNewSession(options = {}) {
        this.conversationHistory = [];
        this.contextTokenSize = 16384;
        this.activeModel = options.activeModel || this.activeModel || '';
        this.selectedMode = options.selectedMode || this.selectedMode || 'hybrid';
        this.pendingToolResults = {};
        this.pendingApprovals = [];
    }

    resetSession() {
        this.startNewSession();
    }

    importSession(jsonString) {
        try {
            const session = JSON.parse(jsonString);
            this.conversationHistory = session.conversationHistory || [];
            this.contextTokenSize = session.contextTokenSize || 16384;
            this.activeModel = session.activeModel || '';
            this.selectedMode = session.selectedMode || 'hybrid';
            this.previousPrompts = session.previousPrompts || [];
            return true;
        } catch (err) {
            logger.log(`Error importing session: ${err.message}`);
            throw err;
        }
    }

    exportSession() {
        return JSON.stringify({
            conversationHistory: this.conversationHistory,
            contextTokenSize: this.contextTokenSize,
            activeModel: this.activeModel,
            selectedMode: this.selectedMode,
            previousPrompts: this.previousPrompts
        }, null, 2);
    }

    getState() {
        return {
            conversationHistory: this.conversationHistory,
            contextTokenSize: this.contextTokenSize,
            activeWorkspace: this.activeWorkspace,
            activeModel: this.activeModel,
            selectedMode: this.selectedMode,
            pendingToolResults: this.pendingToolResults,
            pendingApprovals: this.pendingApprovals,
            previousPrompts: this.previousPrompts,
            savedSessionMetadata: this.savedSessionMetadata,
            availableModels: this.availableModels
        };
    }



    async continueSession(prompt, webviewClient) {
        this.currentRequest = prompt;
        if (prompt) {
            this.previousPrompts.push(prompt);
        }

        try {
            const isFirstMessage = (this.conversationHistory.filter(m => m.role === 'user').length === 0);
            if (this.conversationHistory.length === 0) {
                this.conversationHistory.push({
                    role: 'system',
                    content: `You are Chatsito, a coding assistant embedded in VS Code.

You help the user understand, modify, debug, and navigate the current workspace.

You must treat the workspace as the source of truth. Do not invent files, APIs, symbols, diagnostics, or test results. If information is missing, use an available tool or say what is missing.

Tool-use rules:
- Use tools when you need project-specific information.
- Prefer precise tools over broad tools.
- Prefer find_definition/find_references/get_context_at_location before broad text search.
- Use read_file only when you know the file is relevant.
- If a tool result is truncated, request narrower context before making strong claims.
- Do not repeat the same tool call with the same arguments.

Code-editing rules:
- For code changes, produce a patch proposal.
- Do not claim a patch was applied unless the tool result confirms it.
- Do not claim code compiles or tests pass unless build/test tool results confirm it.
- Keep patches minimal and targeted unless the user asks for a larger refactor.

- Be concise.
- Mention relevant files and line numbers when possible.
- Explain uncertainty clearly.

Tool result contract:
- Tool results are the authoritative source of truth.
- Do NOT assume a command or patch succeeded unless the tool returns a success message.
- If a tool fails, adapt your strategy based on the error message.

Approval contract:
- Patches require user approval. If the user denies permission, the tool will return a cancellation error. Respect this and do not try to blindly apply the same patch again.`
                });
            }

            let promptContent = prompt;
            if (isFirstMessage && prompt) {
                webviewClient.sendProgress('Collecting initial prompt context...');
                let initialContext = "No active editor context found.";
                const editor = vscode.window.activeTextEditor;
                if (editor) {
                    const filePath = editor.document.uri.fsPath;
                    const lineNumber = editor.selection.active.line + 1;
                    initialContext = await getInitialPromptContext(filePath, lineNumber, 2);
                }
                promptContent = `[Context]\n${initialContext}\n\n[User Prompt]\n${prompt}`;
            } else if (!isFirstMessage && prompt) {
                const editor = vscode.window.activeTextEditor;
                if (editor) {
                    const filePath = editor.document.uri.fsPath;
                    const lineNumber = editor.selection.active.line + 1;
                    const relPath = vscode.workspace.asRelativePath(filePath);
                    const lightweightContext = `[Active File: ${relPath}, Cursor Line: ${lineNumber}]`;
                    promptContent = `${lightweightContext}\n\n${prompt}`;
                }
            }

            if (prompt) {
                this.conversationHistory.push({
                    role: 'user',
                    content: promptContent,
                    displayContent: prompt
                });
            }

            webviewClient.sendStateUpdate();

            let isThinking = true;
            let iterationCount = 0;
            const MAX_ITERATIONS = this.chatsitoApiClient.maxToolIterations || 20;
            let previousToolCallsStr = '';
            let duplicateCount = 0;

            while (isThinking) {
                if (iterationCount >= MAX_ITERATIONS) {
                    this.conversationHistory.push({
                        role: 'user',
                        content: "Error: Max tool execution limit reached. Please provide a final answer or explain what went wrong."
                    });
                    webviewClient.sendStateUpdate();
                    webviewClient.sendError("Chatsito reached the maximum number of consecutive tool calls.");
                    break;
                }
                iterationCount++;

                webviewClient.sendProgress('Chatsito is thinking...');

                logger.log(`[ChatSessionManager] Posting HTTP request to Chatsito Web API. Messages count: ${this.conversationHistory.length}.`);

                const result = await this.chatsitoApiClient.sendChat(
                    this.conversationHistory,
                    this.toolManager.getToolsDefinition()
                );

                if (result.success && result.message) {
                    let msgLog = `[ChatSessionManager] Received message from model.`;
                    logger.log(msgLog);
                    this.conversationHistory.push(result.message);
                    webviewClient.sendStateUpdate();

                    if (result.doneReason && result.doneReason !== 'stop') {
                        let criticalMsg = `Model generation stopped prematurely. Done Reason: '${result.doneReason}'.`;
                        if (result.doneReason === 'length') {
                            let tokenEstimate = -1;
                            const thinkingText = result.message.thinking || result.message.reasoning_content || '';
                            if (thinkingText) {
                                tokenEstimate = await this.chatsitoApiClient.estimateTokens(thinkingText);
                            }
                            criticalMsg += `\n- Context: The model hit the generation token limit (context size: ${result.contextTokenSize}, predict size: ${result.predictTokenSize}).`;
                            criticalMsg += `\n- Thinking Token Estimate: ~${tokenEstimate} tokens.`;
                            criticalMsg += `\n- Suggestion: increase context size, thinking size, or disable thinking/reasoning if not required.`;
                        }
                        // if (result.message.thinking) {
                        //     criticalMsg += `\n- Last truncated thinking block: "${result.message.thinking.slice(-300)}"`;
                        // } else if (result.message.reasoning_content) {
                        //     criticalMsg += `\n- Last truncated reasoning content: "${result.message.reasoning_content.slice(-300)}"`;
                        // }
                        logger.logCritical(criticalMsg);
                    }

                    if (result.message.tool_calls && result.message.tool_calls.length > 0) {
                        const currentToolCallsStr = result.message.tool_calls.map(t => {
                            const func = t.function || t;
                            return `${func.name}:${JSON.stringify(func.arguments || {})}`;
                        }).join('|');
                        if (currentToolCallsStr === previousToolCallsStr) {
                            duplicateCount++;
                        } else {
                            duplicateCount = 0;
                            previousToolCallsStr = currentToolCallsStr;
                        }

                        if (duplicateCount >= 3) {
                            this.conversationHistory.push({
                                role: 'user',
                                content: "Error: You are repeatedly making the exact same tool calls. Please review your strategy and try something else."
                            });
                            webviewClient.sendStateUpdate();
                            continue;
                        }

                        let hasExecutedTool = false;

                        for (const toolCall of result.message.tool_calls) {
                            if (toolCall.function) {
                                const routerResult = await ResponseRouter.routeToolCall(toolCall, webviewClient, this.toolManager, this.selectedMode);

                                if (routerResult.action === 'tool_executed') {
                                    this.conversationHistory.push({
                                        role: 'tool',
                                        name: routerResult.toolName,
                                        content: typeof routerResult.toolResult === 'string' ? routerResult.toolResult : logger.formatJson(routerResult.toolResult)
                                    });
                                    hasExecutedTool = true;
                                }
                            }
                        }

                        webviewClient.sendStateUpdate();

                        if (!hasExecutedTool) {
                            logger.log(`[ChatSessionManager] No tools were executed from the response. Terminating cycle.`);
                            isThinking = false;
                        }
                    } else {
                        logger.log(`[ChatSessionManager] Response contains no tool calls. Terminating cycle.`);
                        isThinking = false;
                    }
                } else {
                    throw new Error(result.error || "An unknown error occurred.");
                }
            }

            webviewClient.sendCycleFinished();
        } catch (error) {
            logger.log(`[ChatSessionManager] Error during chat cycle: ${error.message}`);
            this.rollbackMessages();
            webviewClient.sendStateUpdate();
            webviewClient.sendError(error.message || "Failed to communicate with the Chatsito API.");
        } finally {
            this.currentRequest = null;
        }
    }

    rollbackMessages() {
        while (this.conversationHistory.length > 0 && this.conversationHistory[this.conversationHistory.length - 1].role !== 'user') {
            this.conversationHistory.pop();
        }
        if (this.conversationHistory.length > 0) {
            this.conversationHistory.pop();
        }
    }


}

module.exports = ChatSessionManager;
