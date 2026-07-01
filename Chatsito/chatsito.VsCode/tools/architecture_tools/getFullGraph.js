const vscode = require('vscode');
const path = require('path');
const getContextAtLocation = require('../core_coding_assistant/getContextAtLocation');
const findEnclosingSymbol = getContextAtLocation.findEnclosingSymbol || function() { return null; }; // Fallback since getContextAtLocation doesn't export findEnclosingSymbol directly! Wait...
function getSymbolKindString(kind) {
    switch (kind) {
        case vscode.SymbolKind.Method: return "Method";
        case vscode.SymbolKind.Function: return "Function";
        case vscode.SymbolKind.Constructor: return "Constructor";
        case vscode.SymbolKind.Class: return "Class";
        case vscode.SymbolKind.Interface: return "Interface";
        case vscode.SymbolKind.Struct: return "Struct";
        case vscode.SymbolKind.Enum: return "Enum";
        case vscode.SymbolKind.Property: return "Property";
        case vscode.SymbolKind.Field: return "Field";
        default: return "Symbol";
    }
}

async function buildGraphRecursive(node, position, visited) {
    const references = await vscode.commands.executeCommand('vscode.executeReferenceProvider', node.uri, position) || [];
    const addedChildrenKeys = new Set();
    
    for (const ref of references) {
        const isDecl = ref.uri.toString() === node.uri.toString() &&
                       ref.range.start.line === position.line;
        if (isDecl) {
            continue;
        }

        try {
            const refSymbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', ref.uri) || [];
            const enclosingCaller = findEnclosingSymbol(refSymbols, ref.range.start.line);

            if (enclosingCaller) {
                const isValidCaller = [
                    vscode.SymbolKind.Method,
                    vscode.SymbolKind.Function,
                    vscode.SymbolKind.Constructor,
                    vscode.SymbolKind.Class,
                    vscode.SymbolKind.Interface,
                    vscode.SymbolKind.Struct,
                    vscode.SymbolKind.Enum,
                    vscode.SymbolKind.Property,
                    vscode.SymbolKind.Field
                ].includes(enclosingCaller.kind);

                if (isValidCaller) {
                    const key = `${ref.uri.toString()}:${enclosingCaller.name}`;
                    
                    if (addedChildrenKeys.has(key)) {
                        continue;
                    }
                    addedChildrenKeys.add(key);

                    if (!visited.has(key)) {
                        visited.add(key);

                        const childNode = {
                            name: enclosingCaller.name,
                            kind: enclosingCaller.kind,
                            uri: ref.uri,
                            line: enclosingCaller.range.start.line + 1,
                            children: []
                        };

                        node.children.push(childNode);
                        await buildGraphRecursive(childNode, enclosingCaller.selectionRange.start, visited);
                    } else {
                        node.children.push({
                            name: `${enclosingCaller.name} [CIRCULAR]`,
                            kind: enclosingCaller.kind,
                            uri: ref.uri,
                            line: enclosingCaller.range.start.line + 1,
                            children: []
                        });
                    }
                }
            }
        } catch (e) {
            // Ignore
        }
    }
}

async function getFullGraph(filePath, line, character) {
    if (!filePath) return "Error: No file path provided.";

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

        const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];
        const enclosingSym = findEnclosingSymbol(symbols, line);
        if (!enclosingSym) {
            return `No enclosing symbol found at line ${line + 1}`;
        }

        const visited = new Set();
        const treeRoot = {
            name: enclosingSym.name,
            kind: enclosingSym.kind,
            uri: uri,
            line: enclosingSym.range.start.line + 1,
            children: []
        };

        visited.add(`${uri.toString()}:${enclosingSym.name}`);
        await buildGraphRecursive(treeRoot, new vscode.Position(line, character), visited);

        let graphText = "";
        function printNode(node, indent = "") {
            const relPath = vscode.workspace.asRelativePath(node.uri);
            const lineInfo = `[${relPath}:${node.line}]`;
            const kindStr = getSymbolKindString(node.kind);
            graphText += `${indent}└─ ${node.name} (${kindStr}) ${lineInfo}\n`;
            for (const child of node.children) {
                printNode(child, indent + "   ");
            }
        }
        
        graphText += `--- full backwards call graph ---\n\n`;
        printNode(treeRoot);
        return graphText;
    } catch (error) {
        return `Error generating graph: ${error.message}`;
    }
}

module.exports = getFullGraph;
