const vscode = require('vscode');
const path = require('path');

async function getSymbolsInFile(filePath) {
    if (!filePath) {
        return "Error: No file path provided.";
    }

    try {
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

        // Open doc first to ensure language services are active
        await vscode.workspace.openTextDocument(uri);
        const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];
        
        if (symbols.length === 0) {
            return `No symbols found in file: ${vscode.workspace.asRelativePath(uri)}`;
        }

        let symbolText = `=== Symbols in ${vscode.workspace.asRelativePath(uri)} ===\n\n`;

        function getSymbolKindString(kind) {
            switch (kind) {
                case vscode.SymbolKind.File: return "File";
                case vscode.SymbolKind.Module: return "Module";
                case vscode.SymbolKind.Namespace: return "Namespace";
                case vscode.SymbolKind.Package: return "Package";
                case vscode.SymbolKind.Class: return "Class";
                case vscode.SymbolKind.Method: return "Method";
                case vscode.SymbolKind.Property: return "Property";
                case vscode.SymbolKind.Field: return "Field";
                case vscode.SymbolKind.Constructor: return "Constructor";
                case vscode.SymbolKind.Enum: return "Enum";
                case vscode.SymbolKind.Interface: return "Interface";
                case vscode.SymbolKind.Function: return "Function";
                case vscode.SymbolKind.Variable: return "Variable";
                case vscode.SymbolKind.Constant: return "Constant";
                case vscode.SymbolKind.String: return "String";
                case vscode.SymbolKind.Number: return "Number";
                case vscode.SymbolKind.Boolean: return "Boolean";
                case vscode.SymbolKind.Array: return "Array";
                case vscode.SymbolKind.Object: return "Object";
                case vscode.SymbolKind.Key: return "Key";
                case vscode.SymbolKind.Null: return "Null";
                case vscode.SymbolKind.EnumMember: return "EnumMember";
                case vscode.SymbolKind.Struct: return "Struct";
                case vscode.SymbolKind.Event: return "Event";
                case vscode.SymbolKind.Operator: return "Operator";
                case vscode.SymbolKind.TypeParameter: return "TypeParameter";
                default: return "Symbol";
            }
        }

        function formatSymbol(sym, indent = "") {
            const kindStr = getSymbolKindString(sym.kind);
            symbolText += `${indent}- [${kindStr}] ${sym.name} (Lines: ${sym.range.start.line + 1} - ${sym.range.end.line + 1})\n`;
            if (sym.children && sym.children.length > 0) {
                for (const child of sym.children) {
                    formatSymbol(child, indent + "  ");
                }
            }
        }

        for (const sym of symbols) {
            formatSymbol(sym);
        }

        return symbolText;
    } catch (error) {
        return `Error getting symbols in file: ${error.message}`;
    }
}

module.exports = getSymbolsInFile;
