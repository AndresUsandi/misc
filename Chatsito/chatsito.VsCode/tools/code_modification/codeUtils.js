const vscode = require('vscode');

const normalizeText = (text) => {
    if (typeof text !== 'string') return '';
    return text.replace(/\r\n/g, '\n');
};

const cleanQuotes = (str) => {
    return str
        .replace(/^""""+/, '"""')
        .replace(/""""+$/, '"""')
        .replace(/^''''+/, "'''")
        .replace(/''''+$/, "'''");
};

const normalizeAndClean = (text) => {
    return cleanQuotes(normalizeText(text));
};

const getRangeText = (doc, startLine, startChar, endLine, endChar) => {
    const maxLine = doc.lineCount - 1;
    const sLine = Math.min(Math.max(0, startLine), maxLine);
    const eLine = Math.min(Math.max(0, endLine), maxLine);
    const sChar = Math.min(Math.max(0, startChar), doc.lineAt(sLine).text.length);
    const eChar = Math.min(Math.max(0, endChar), doc.lineAt(eLine).text.length);

    return doc.getText(new vscode.Range(
        new vscode.Position(sLine, sChar),
        new vscode.Position(eLine, eChar)
    ));
};

const findUniqueRange = (doc, expectedText) => {
    const fullText = doc.getText().replace(/\r\n/g, '\n');
    const normalizedExpected = expectedText.replace(/\r\n/g, '\n');
    const index = fullText.indexOf(normalizedExpected);
    const lastIndex = fullText.lastIndexOf(normalizedExpected);

    if (index !== -1 && index === lastIndex) {
        const before = fullText.substring(0, index);
        const linesBefore = before.split('\n');
        const startLine = linesBefore.length - 1;
        const startChar = linesBefore[linesBefore.length - 1].length;

        const expectedLines = normalizedExpected.split('\n');
        const endLine = startLine + expectedLines.length - 1;
        const endChar = expectedLines.length > 1
            ? expectedLines[expectedLines.length - 1].length
            : startChar + normalizedExpected.length;

        return { startLine, startChar, endLine, endChar };
    }
    return null;
};

/**
 * Validates the missing parameters for a tool by checking schemas.
 */
function validateRequiredParams(toolName, args) {
    if (!args) {
        return "Error: Missing required parameters.";
    }
    try {
        const ToolDefinitionProvider = require('../../ToolDefinitionProvider');
        const toolDef = ToolDefinitionProvider.getToolDefinition(toolName);
        if (toolDef && toolDef.schema && toolDef.schema.parameters && toolDef.schema.parameters.properties) {
            const properties = toolDef.schema.parameters.properties;
            const required = toolDef.schema.parameters.required || [];
            const missing = required.filter(field => args[field] === undefined || args[field] === null || args[field] === '');
            
            if (missing.length > 0) {
                let errors = "Error: Missing required parameters:\n";
                for (const field of missing) {
                    const fieldDef = properties[field];
                    const desc = fieldDef ? fieldDef.description : '';
                    errors += `${field} - ${desc}\n`;
                }
                return errors;
            }
        }
    } catch (e) {
        return `Error: ${e.message}`;
    }
    return null;
}

module.exports = {
    normalizeText,
    cleanQuotes,
    normalizeAndClean,
    getRangeText,
    findUniqueRange,
    validateRequiredParams
};
