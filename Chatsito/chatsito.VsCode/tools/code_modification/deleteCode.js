const vscode = require('vscode');
const path = require('path');
const {
    normalizeAndClean,
    getRangeText,
    findUniqueRange,
    validateRequiredParams
} = require('./codeUtils');

async function deleteCode(args) {
    let filePath, startLine, startChar, endLine, endChar, expectedOriginalText;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ filePath, startLine, startChar, endLine, endChar, expectedOriginalText } = args);
    } else {
        filePath = arguments[0];
        startLine = arguments[1];
        startChar = arguments[2];
        endLine = arguments[3];
        endChar = arguments[4];
        expectedOriginalText = arguments[5];
    }

    const normalizedArgs = { filePath, startLine, startChar, endLine, endChar, expectedOriginalText };
    const validationErr = validateRequiredParams("deleteCode", normalizedArgs);
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

    const normalizedExpected = normalizeAndClean(expectedOriginalText).trim();

    try {
        const PathResolver = require('../../PathResolver');
        const uri = vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));
        const doc = await vscode.workspace.openTextDocument(uri);

        let chosenStartLine = null;
        let chosenStartChar = null;
        let chosenEndLine = null;
        let chosenEndChar = null;

        // 1. Try 1-based indexing
        const start1 = start_line - 1;
        const char1 = start_char - 1;
        const end1 = end_line - 1;
        const char1End = end_char - 1;

        const text1 = getRangeText(doc, start1, char1, end1, char1End);
        if (normalizeAndClean(text1) === normalizedExpected) {
            chosenStartLine = start1;
            chosenStartChar = char1;
            chosenEndLine = end1;
            chosenEndChar = char1End;
        } else {
            // 2. Try 0-based indexing fallback
            const text0 = getRangeText(doc, start_line, start_char, end_line, end_char);
            if (normalizeAndClean(text0) === normalizedExpected) {
                chosenStartLine = start_line;
                chosenStartChar = start_char;
                chosenEndLine = end_line;
                chosenEndChar = end_char;
            } else {
                // 3. Try unique expected text scan fallback
                const uniqueRange = findUniqueRange(doc, expectedOriginalText);
                if (uniqueRange) {
                    chosenStartLine = uniqueRange.startLine;
                    chosenStartChar = uniqueRange.startChar;
                    chosenEndLine = uniqueRange.endLine;
                    chosenEndChar = uniqueRange.endChar;
                }
            }
        }

        if (chosenStartLine === null) {
            const currentText = getRangeText(doc, start1, char1, end1, char1End);
            return `Error: Stale edit detected in ${vscode.workspace.asRelativePath(uri)}. The text at the specified range has changed. Expected: "${expectedOriginalText}", Found: "${currentText}". Please refresh your context and try again.`;
        }

        const edit = new vscode.WorkspaceEdit();
        const range = new vscode.Range(new vscode.Position(chosenStartLine, chosenStartChar), new vscode.Position(chosenEndLine, chosenEndChar));
        edit.delete(uri, range);
        
        return {
            edit: edit,
            successMessage: `Successfully deleted code at ${vscode.workspace.asRelativePath(uri)} from line ${chosenStartLine + 1} to ${chosenEndLine + 1}`
        };
    } catch (e) {
        return `Error deleting code: ${e.message}`;
    }
}

module.exports = deleteCode;
