const vscode = require('vscode');

let logChannel = null;

function initLogger(context) {
    if (!logChannel) {
        logChannel = vscode.window.createOutputChannel("Chatsito Logs");
        context.subscriptions.push(logChannel);
    }
    return logChannel;
}

function getLogChannel() {
    return logChannel;
}

function log(message) {
    if (logChannel) {
        logChannel.appendLine(message);
    }
}

function formatJson(obj) {
    if (obj === undefined) return 'undefined';
    if (obj === null) return 'null';
    try {
        return JSON.stringify(obj, null, 2)
            .replace(/(?<!\\)\\n/g, '\n')
            .replace(/(?<!\\)\\r/g, '\r')
            .replace(/(?<!\\)\\t/g, '\t')
            .replace(/(?<!\\)\\"/g, '"')
            .replace(/\\\\/g, '\\');
    } catch (e) {
        return String(obj);
    }
}

module.exports = {
    initLogger,
    getLogChannel,
    log,
    formatJson
};
