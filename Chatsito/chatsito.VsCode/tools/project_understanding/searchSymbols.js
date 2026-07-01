const vscode = require('vscode');

async function searchSymbols(query) {
    if (!query || query.trim() === '') {
        return "Error: No query provided.";
    }

    try {
        const parts = query.split(/\s+/);
        let nameQuery = '';
        let filterKind = null;
        let filterContainer = null;

        for (const part of parts) {
            if (part.startsWith('kind:')) {
                filterKind = part.substring(5).toLowerCase();
            } else if (part.startsWith('container:')) {
                filterContainer = part.substring(10).toLowerCase();
            } else {
                nameQuery += (nameQuery ? ' ' : '') + part;
            }
        }

        if (!nameQuery) {
            nameQuery = query;
        }

        const symbols = await vscode.commands.executeCommand('vscode.executeWorkspaceSymbolProvider', nameQuery) || [];
        
        // Apply filters
        let filtered = symbols;
        if (filterKind) {
            filtered = filtered.filter(sym => {
                const kindStr = (vscode.SymbolKind[sym.kind] || '').toLowerCase();
                return kindStr.includes(filterKind);
            });
        }
        if (filterContainer) {
            filtered = filtered.filter(sym => {
                const containerStr = (sym.containerName || '').toLowerCase();
                return containerStr.includes(filterContainer);
            });
        }

        if (filtered.length === 0) {
            return `No symbols found matching query: ${query}`;
        }

        let output = `=== Symbols Search Results (${filtered.length} matches) ===\n\n`;
        for (const sym of filtered) {
            const relPath = vscode.workspace.asRelativePath(sym.location.uri);
            const line = sym.location.range.start.line + 1;
            const kind = vscode.SymbolKind[sym.kind] || 'Unknown';
            const container = sym.containerName ? ` (in ${sym.containerName})` : '';
            output += `Symbol: ${sym.name}${container}\n`;
            output += `  Kind: ${kind}\n`;
            output += `  Location: ${relPath}:${line}\n\n`;
        }

        return output.trim();
    } catch (error) {
        return `Error searching symbols: ${error.message}`;
    }
}

module.exports = searchSymbols;
