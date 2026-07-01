const vscode = require('vscode');

async function lookupApi(symbolName) {
    if (!symbolName) return "Error: Missing symbolName parameter.";

    try {
        const query = String(symbolName);
        
        // Use VS Code's built-in symbol provider
        const symbols = await vscode.commands.executeCommand('vscode.executeWorkspaceSymbolProvider', query);

        if (!symbols || symbols.length === 0) {
            return `No API definitions found for symbol: "${query}".`;
        }

        // Limit to top 10 results to avoid massive output
        const results = symbols.slice(0, 10);
        let output = `=== API Lookup Results for "${query}" ===\n\n`;

        results.forEach((sym, index) => {
            const kind = vscode.SymbolKind[sym.kind] || 'Unknown';
            const filePath = vscode.workspace.asRelativePath(sym.location.uri.fsPath);
            const line = sym.location.range.start.line + 1; // 1-indexed

            output += `${index + 1}. [${kind}] ${sym.name}\n`;
            if (sym.containerName) {
                output += `   Container: ${sym.containerName}\n`;
            }
            output += `   Location: ${filePath}:${line}\n\n`;
        });

        if (symbols.length > 10) {
            output += `... and ${symbols.length - 10} more results.\n`;
        }

        return output;

    } catch (e) {
        return `Error looking up API: ${e.message}`;
    }
}

module.exports = lookupApi;
