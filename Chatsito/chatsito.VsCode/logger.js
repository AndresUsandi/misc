const vscode = require('vscode');

let logChannel = null;
let criticalChannel = null;
let debugChannel = null;

function initLogger(context) {
    if (!logChannel) {
        logChannel = vscode.window.createOutputChannel("Chatsito Logs");
        context.subscriptions.push(logChannel);
    }
    if (!criticalChannel) {
        criticalChannel = vscode.window.createOutputChannel("Chatsito Logs - Critical");
        context.subscriptions.push(criticalChannel);
    }
    if (!debugChannel) {
        debugChannel = vscode.window.createOutputChannel("Chatsito Logs - Debug");
        context.subscriptions.push(debugChannel);
    }
    return logChannel;
}

function getLogChannel() {
    return logChannel;
}

function getCriticalChannel() {
    return criticalChannel;
}

function getDebugChannel() {
    return debugChannel;
}

function log(message) {
    if (logChannel) {
        logChannel.appendLine(message);
    }
}

function logCritical(message) {
    if (logChannel) {
        logChannel.appendLine(`[CRITICAL] ${message}`);
    }
    if (criticalChannel) {
        criticalChannel.appendLine(message);
    }
}

function logDebug(message) {
    if (debugChannel) {
        debugChannel.appendLine(message);
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
    getCriticalChannel,
    getDebugChannel,
    log,
    logCritical,
    logDebug,
    formatJson
};
