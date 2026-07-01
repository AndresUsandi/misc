const vscode = require('vscode');
const path = require('path');

function findEnclosingSymbol(symbols, line) {
    for (const sym of symbols) {
        if (sym.range.start.line <= line && sym.range.end.line >= line) {
            if (sym.children && sym.children.length > 0) {
                const child = findEnclosingSymbol(sym.children, line);
                if (child) return child;
            }
            return sym;
        }
    }
    return null;
}

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
            console.error(e);
        }
    }
}

async function getFullGraphContext(filePath, lineNumber, characterNumber) {
    const line = lineNumber - 1;
    const character = (characterNumber || 1) - 1;
    
    let uri;
    if (path.isAbsolute(filePath)) {
        uri = vscode.Uri.file(filePath);
    } else {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            return "No workspace folder open.";
        }
        uri = vscode.Uri.file(path.join(workspaceFolder.uri.fsPath, filePath));
    }

    try {
        const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];
        const enclosingSym = findEnclosingSymbol(symbols, line);
        if (!enclosingSym) {
            return `No enclosing symbol found at line ${lineNumber}`;
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
    } catch (err) {
        return `Failed to generate call graph for ${filePath}: ${err.message}`;
    }
}

module.exports = getFullGraphContext;
