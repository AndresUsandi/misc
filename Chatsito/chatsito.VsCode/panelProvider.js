const vscode = require('vscode');
const { getWebviewContent } = require('./webviewContent');
const WebviewClient = require('./WebviewClient');

class ChatsitoPanel {
    static currentPanel = undefined;
    static viewType = 'chatsitoWebview';

    static createOrShow(extensionPath, sessionManager) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ChatsitoPanel.currentPanel) {
            ChatsitoPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            ChatsitoPanel.viewType,
            'Chatsito Chat',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.file(extensionPath)]
            }
        );

        ChatsitoPanel.currentPanel = new ChatsitoPanel(panel, extensionPath, sessionManager);
    }

    constructor(panel, extensionPath, sessionManager) {
        this._panel = panel;
        this._extensionPath = extensionPath;
        this._sessionManager = sessionManager;
        this._update();
        new WebviewClient(this._panel.webview, this._sessionManager);

        this._panel.onDidDispose(() => this.dispose(), null, []);
    }

    dispose() {
        ChatsitoPanel.currentPanel = undefined;
        this._panel.dispose();
    }

    _update() {
        this._panel.webview.html = getWebviewContent(this._panel.webview, this._extensionPath);
    }
}

module.exports = ChatsitoPanel;

