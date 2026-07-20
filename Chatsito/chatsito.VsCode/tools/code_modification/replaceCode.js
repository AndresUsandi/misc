const vscode = require('vscode');
const path = require('path');
const {
    normalizeAndClean,
    getRangeText,
    findUniqueRange,
    validateRequiredParams
} = require('./codeUtils');

async function replaceCode(args) {
    let filePath, startLine, startChar, endLine, endChar, textToReplace, expectedOriginalText;
    if (args && typeof args === 'object' && !Array.isArray(args)) {
        ({ filePath, startLine, startChar, endLine, endChar, textToReplace, expectedOriginalText } = args);
    } else {
        filePath = arguments[0];
        startLine = arguments[1];
        startChar = arguments[2];
        endLine = arguments[3];
        endChar = arguments[4];
        textToReplace = arguments[5];
        expectedOriginalText = arguments[6];
    }

    const normalizedArgs = { filePath, startLine, startChar, endLine, endChar, textToReplace, expectedOriginalText };
    const validationErr = validateRequiredParams("replaceCode", normalizedArgs);
    if (validationErr) {
        return validationErr;
    }

    const start_line = parseInt(startLine, 10);
    const start_char = (startChar === undefined || startChar === null || startChar === '') ? 1 : parseInt(startChar, 10);
    const end_line = parseInt(endLine, 10);
    const end_char = (endChar === undefined || endChar === null || endChar === '') ? 999999 : parseInt(endChar, 10);

    if (isNaN(start_line) || isNaN(start_char) || isNaN(end_line) || isNaN(end_char)) {
        return "Error: Coordinates start_line, start_char, end_line, and end_char must be valid integers.";
    }

    const normalizedToReplace = normalizeAndClean(textToReplace).trim();
    const normalizedExpected = normalizeAndClean(expectedOriginalText).trim();
    if (normalizedToReplace === normalizedExpected) {
        return `Error: 'textToReplace' is identical to 'expectedOriginalText'. You must provide the NEW modified code in 'textToReplace'. The replacement was rejected because it would result in no changes.`;
    }

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

        // Constrain resolved character offsets to actual line bounds
        const startLineTextLength = doc.lineAt(chosenStartLine).text.length;
        const endLineTextLength = doc.lineAt(chosenEndLine).text.length;
        chosenStartChar = Math.min(Math.max(0, chosenStartChar), startLineTextLength);
        chosenEndChar = Math.min(Math.max(0, chosenEndChar), endLineTextLength);

        let startCharToUse = chosenStartChar;
        if (chosenStartChar > 0 && chosenStartLine < doc.lineCount) {
            const linePrefix = doc.lineAt(chosenStartLine).text.substring(0, chosenStartChar);
            if (linePrefix.trim() === '' && /^\s/.test(textToReplace)) {
                startCharToUse = 0;
            }
        }

        const edit = new vscode.WorkspaceEdit();
        const range = new vscode.Range(new vscode.Position(chosenStartLine, startCharToUse), new vscode.Position(chosenEndLine, chosenEndChar));
        edit.replace(uri, range, textToReplace);

        return {
            edit: edit,
            successMessage: `Successfully replaced code at ${vscode.workspace.asRelativePath(uri)} from line ${chosenStartLine + 1} to ${chosenEndLine + 1}`
        };
    } catch (e) {
        return `Error replacing code: ${e.message}`;
    }
}

module.exports = replaceCode;
