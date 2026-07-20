const vscode = require('vscode');
const path = require('path');
const { validateRequiredParams } = require('./codeUtils');

async function extractMethod(args) {
    let filePath, startLine, startChar, endLine, endChar, newMethodName;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ filePath, startLine, startChar, endLine, endChar, newMethodName } = args);
    } else {
        filePath = arguments[0];
        startLine = arguments[1];
        startChar = arguments[2];
        endLine = arguments[3];
        endChar = arguments[4];
        newMethodName = arguments[5];
    }

    const normalizedArgs = { filePath, startLine, startChar, endLine, endChar, newMethodName };
    const validationErr = validateRequiredParams("extractMethod", normalizedArgs);
    if (validationErr) {
        return validationErr;
    }

    const start_line = parseInt(startLine, 10);
    const start_char = parseInt(startChar, 10);
    const end_line = parseInt(endLine, 10);
    const end_char = parseInt(endChar, 10);

    if (isNaN(start_line) || isNaN(start_char) || isNaN(end_line) || isNaN(end_char)) {
        return "Error: Coordinates start_line, start_char, end_line, and end_char must be valid integers.";
    }

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));
        const doc = await vscode.workspace.openTextDocument(uri);

        // Try 1-based indexing first
        const sLine1 = start_line - 1;
        const sChar1 = start_char - 1;
        const eLine1 = end_line - 1;
        const eChar1 = end_char - 1;

        const maxLine = doc.lineCount - 1;
        const sLine1Clamped = Math.min(Math.max(0, sLine1), maxLine);
        const eLine1Clamped = Math.min(Math.max(0, eLine1), maxLine);
        const sChar1Clamped = Math.min(Math.max(0, sChar1), doc.lineAt(sLine1Clamped).text.length);
        const eChar1Clamped = Math.min(Math.max(0, eChar1), doc.lineAt(eLine1Clamped).text.length);

        const range1 = new vscode.Range(new vscode.Position(sLine1Clamped, sChar1Clamped), new vscode.Position(eLine1Clamped, eChar1Clamped));
        let codeActions = await vscode.commands.executeCommand('vscode.executeCodeActionProvider', uri, range1) || [];
        let extractAction = codeActions.find(a => a.title.toLowerCase().includes('extract') && (a.title.toLowerCase().includes('method') || a.title.toLowerCase().includes('function')));

        // Fallback 1: Try 0-based indexing if different
        if (!extractAction && (sLine1 !== start_line || sChar1 !== start_char || eLine1 !== end_line || eChar1 !== end_char)) {
            const sLine0Clamped = Math.min(Math.max(0, start_line), maxLine);
            const eLine0Clamped = Math.min(Math.max(0, end_line), maxLine);
            const sChar0Clamped = Math.min(Math.max(0, start_char), doc.lineAt(sLine0Clamped).text.length);
            const eChar0Clamped = Math.min(Math.max(0, end_char), doc.lineAt(eLine0Clamped).text.length);

            const range0 = new vscode.Range(new vscode.Position(sLine0Clamped, sChar0Clamped), new vscode.Position(eLine0Clamped, eChar0Clamped));
            const codeActions0 = await vscode.commands.executeCommand('vscode.executeCodeActionProvider', uri, range0) || [];
            extractAction = codeActions0.find(a => a.title.toLowerCase().includes('extract') && (a.title.toLowerCase().includes('method') || a.title.toLowerCase().includes('function')));
        }

        // Fallback 2: Try original backup range (shifting 1-based range by 1 line)
        if (!extractAction && sLine1 + 1 < doc.lineCount && eLine1 + 1 < doc.lineCount) {
            const backupRange = new vscode.Range(new vscode.Position(sLine1 + 1, sChar1Clamped), new vscode.Position(eLine1 + 1, eChar1Clamped));
            const backupActions = await vscode.commands.executeCommand('vscode.executeCodeActionProvider', uri, backupRange) || [];
            extractAction = backupActions.find(a => a.title.toLowerCase().includes('extract') && (a.title.toLowerCase().includes('method') || a.title.toLowerCase().includes('function')));
        }

        if (extractAction) {
            if (extractAction.edit) {
                return {
                    edit: extractAction.edit,
                    successMessage: `Successfully applied extract method refactoring. Extracted method may need to be manually renamed to '${newMethodName}'.`
                };
            } else if (extractAction.command) {
                return {
                    command: extractAction.command.command,
                    args: extractAction.command.arguments || [],
                    successMessage: `Executed extract method command. You may need to rename the new method to '${newMethodName}'.`
                };
            }
        }
        
        return `No automated extract method refactoring available for the selected range.`;
    } catch (e) {
        return `Error extracting method: ${e.message}`;
    }
}

module.exports = extractMethod;
