const vscode = require('vscode');
const logger = require('./logger');

class WebviewClient {
    constructor(webview, sessionManager) {
        this.webview = webview;
        this.sessionManager = sessionManager;
        this.sessionManager.webviewClient = this;
        this.setupMessageListener();
    }

    setupMessageListener() {
        this.webview.onDidReceiveMessage(async (message) => {
            if (message.command === 'log_debug') {
                logger.log(message.message);
                return;
            }

            let logMsg = `[Chatsito Client Host] Received command: '${message.command}'`;
            logger.log(logMsg);

            try {
                switch (message.command) {
                    case 'get_session_state': {
                        this.sendStateUpdate();
                        break;
                    }
                    case 'submit_prompt': {
                        const prompt = message.arguments?.prompt || '';
                        await this.sessionManager.continueSession(prompt, this);
                        break;
                    }
                    case 'clear_chat': {
                        this.sessionManager.resetSession();
                        this.sendStateUpdate();
                        break;
                    }
                    case 'save_session': {
                        const name = message.arguments?.name;
                        await this.sessionManager.saveSession(name);
                        this.sendStateUpdate();
                        vscode.window.showInformationMessage(`Session saved successfully.`);
                        break;
                    }
                    case 'restore_session': {
                        const sessionId = message.arguments?.sessionId;
                        const success = await this.sessionManager.restoreSession(sessionId);
                        if (success) {
                            this.sendStateUpdate();
                            vscode.window.showInformationMessage(`Session restored.`);
                        } else {
                            vscode.window.showErrorMessage(`Failed to restore session.`);
                        }
                        break;
                    }
                    case 'delete_session': {
                        const sessionId = message.arguments?.sessionId;
                        await this.sessionManager.deleteSavedSession(sessionId);
                        this.sendStateUpdate();
                        vscode.window.showInformationMessage(`Session deleted.`);
                        break;
                    }
                    case 'export_session': {
                        const json = this.sessionManager.exportSession();
                        this.postMessage('exportResult', { json });
                        break;
                    }
                    case 'import_session': {
                        const json = message.arguments?.json;
                        if (json) {
                            this.sessionManager.importSession(json);
                            this.sendStateUpdate();
                            vscode.window.showInformationMessage(`Session imported successfully.`);
                        }
                        break;
                    }
                    case 'change_model': {
                        const model = message.arguments?.model;
                        if (model) {
                            this.sessionManager.activeModel = model;
                            this.sendStateUpdate();
                        }
                        break;
                    }
                    case 'change_mode': {
                        const mode = message.arguments?.mode;
                        if (mode) {
                            if (mode === 'admin') {
                                vscode.window.showWarningMessage(
                                    "Warning: Admin-Mode is unrestrained and will execute anything the LLM asks for, even if it is harmful to the system. Are you sure you want to enable this mode?",
                                    { modal: true },
                                    "Accept"
                                ).then(selection => {
                                    if (selection === "Accept") {
                                        this.sessionManager.selectedMode = mode;
                                    }
                                    this.sendStateUpdate();
                                });
                            } else {
                                this.sessionManager.selectedMode = mode;
                                this.sendStateUpdate();
                            }
                        }
                        break;
                    }
                }
            } catch (err) {
                logger.log(`Error processing command ${message.command}: ${err.message}`);
                this.sendError(err.message);
            }
        });
    }

    postMessage(command, payload = {}) {
        if (this.webview) {
            this.webview.postMessage({ command, ...payload });
        }
    }

    sendStateUpdate() {
        this.postMessage('stateUpdate', { state: this.sessionManager.getState() });
    }

    sendProgress(text) {
        this.postMessage('progress', { text });
    }

    sendError(message) {
        this.postMessage('error', { message });
    }

    sendCycleFinished() {
        this.postMessage('cycleFinished');
    }
}

module.exports = WebviewClient;
