const vscode = require('vscode');
const logger = require('./logger');
const ChatsitoSidebarProvider = require('./sidebarProvider');
const ChatsitoPanel = require('./panelProvider');
const ChatSessionManager = require('./ChatSessionManager');

function activate(context) {
    logger.initLogger(context);

    const sessionManager = new ChatSessionManager(context);

    let openChatCommand = vscode.commands.registerCommand('chatsito.openChat', () => {
        ChatsitoPanel.createOrShow(context.extensionPath, sessionManager);
    });
    context.subscriptions.push(openChatCommand);

    let evaluateHumanEvalCommand = vscode.commands.registerCommand('chatsito.evaluateHumanEval', async () => {
        const evaluateHumanEval = require('./scripts/evaluateHumanEval');
        await evaluateHumanEval(sessionManager, context.extensionPath);
    });
    context.subscriptions.push(evaluateHumanEvalCommand);

    const provider = new ChatsitoSidebarProvider(context.extensionPath, sessionManager);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('chatsito.sidebarView', provider, {
            webviewOptions: {
                retainContextWhenHidden: true
            }
        })
    );
}

function deactivate() { }

module.exports = {
    activate,
    deactivate
};

