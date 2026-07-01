const vscode = require('vscode');
const { getWebviewContent } = require('./webviewContent');
const WebviewClient = require('./WebviewClient');

class ChatsitoSidebarProvider {
    constructor(extensionPath, sessionManager) {
        this._extensionPath = extensionPath;
        this._sessionManager = sessionManager;
    }

    resolveWebviewView(webviewView, context, _token) {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [vscode.Uri.file(this._extensionPath)]
        };

        webviewView.webview.html = getWebviewContent(webviewView.webview, this._extensionPath);
        new WebviewClient(webviewView.webview, this._sessionManager);
    }
}

module.exports = ChatsitoSidebarProvider;

