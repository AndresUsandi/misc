const vscode = require('vscode');

async function findSymbol(symbolName) {
    if (!symbolName || symbolName.trim() === '') {
        return "Error: No symbol name provided.";
    }

    try {
        const symbols = await vscode.commands.executeCommand('vscode.executeWorkspaceSymbolProvider', symbolName) || [];
        
        if (symbols.length === 0) {
            return `No symbols found matching: ${symbolName}`;
        }

        // Sort exact match of name first, then by alphabetical name
        const sortedSymbols = [...symbols].sort((a, b) => {
            const aExact = a.name === symbolName;
            const bExact = b.name === symbolName;
            if (aExact && !bExact) return -1;
            if (!aExact && bExact) return 1;
            return a.name.localeCompare(b.name);
        });

        let output = `=== Symbols Found (${sortedSymbols.length} matches) ===\n\n`;
        for (const sym of sortedSymbols) {
            const relPath = vscode.workspace.asRelativePath(sym.location.uri);
            const line = sym.location.range.start.line + 1;
            const kind = vscode.SymbolKind[sym.kind] || 'Unknown';
            const container = sym.containerName ? ` (in ${sym.containerName})` : '';
            output += `Name: ${sym.name}${container}\n`;
            output += `  Kind: ${kind}\n`;
            output += `  Location: ${relPath}:${line}\n\n`;
        }

        return output.trim();
    } catch (error) {
        return `Error finding symbol: ${error.message}`;
    }
}

module.exports = findSymbol;
