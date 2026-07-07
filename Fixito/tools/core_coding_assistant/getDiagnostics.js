import vscode from '../../vscode.js';
import path from 'path';

async function getDiagnostics(filePath) {
    try {
        let diagnostics;
        if (filePath) {
            let uri;
            if (path.isAbsolute(filePath)) {
                uri = vscode.Uri.file(filePath);
            } else {
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (workspaceFolders && workspaceFolders.length > 0) {
                    uri = vscode.Uri.file(path.resolve(workspaceFolders[0].uri.fsPath, filePath));
                } else {
                    return `Error: Could not resolve relative path '${filePath}' because no workspace folders are open.`;
                }
            }
            diagnostics = [[uri, vscode.languages.getDiagnostics(uri)]];
        } else {
            diagnostics = vscode.languages.getDiagnostics();
        }

        if (!diagnostics || diagnostics.length === 0) {
            return "No diagnostics found in workspace.";
        }

        let output = `=== Diagnostics ===\n\n`;
        let totalCount = 0;

        for (const [uri, diagList] of diagnostics) {
            if (!diagList || diagList.length === 0) continue;
            
            const relPath = vscode.workspace.asRelativePath(uri);
            output += `File: ${relPath}\n`;
            
            for (const diag of diagList) {
                totalCount++;
                const severityStr = getSeverityString(diag.severity);
                output += `  [${severityStr}] Line ${diag.range.start.line + 1}: ${diag.message} (${diag.source || 'Unknown source'})\n`;
            }
            output += `\n`;
        }

        if (totalCount === 0) {
            return "No compiler or linter errors/warnings found.";
        }

        return output;
    } catch (error) {
        return `Error getting diagnostics: ${error.message}`;
    }
}

function getSeverityString(severity) {
    switch (severity) {
        case vscode.DiagnosticSeverity.Error: return "Error";
        case vscode.DiagnosticSeverity.Warning: return "Warning";
        case vscode.DiagnosticSeverity.Information: return "Info";
        case vscode.DiagnosticSeverity.Hint: return "Hint";
        default: return "Diagnostic";
    }
}

export default getDiagnostics;
