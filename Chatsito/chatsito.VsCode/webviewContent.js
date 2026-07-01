const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

function getWebviewContent(webview, extensionPath) {
    const htmlPath = path.join(extensionPath, 'webview.html');
    let html = fs.readFileSync(htmlPath, 'utf8');

    const uiUri = webview.asWebviewUri(vscode.Uri.file(path.join(extensionPath, 'webviewUi.js')));
    const apiUri = webview.asWebviewUri(vscode.Uri.file(path.join(extensionPath, 'webviewApi.js')));
    const jsUri = webview.asWebviewUri(vscode.Uri.file(path.join(extensionPath, 'webview.js')));

    html = html.replace('{{webviewUiJsUri}}', uiUri.toString());
    html = html.replace('{{webviewApiJsUri}}', apiUri.toString());
    html = html.replace('{{webviewJsUri}}', jsUri.toString());

    return html;
}

module.exports = { getWebviewContent };

