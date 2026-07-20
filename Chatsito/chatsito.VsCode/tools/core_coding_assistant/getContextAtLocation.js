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

async function getContextAtLocation(filePath, line, character, callStackLevel = 2) {
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

        const doc = await vscode.workspace.openTextDocument(uri);
        const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];
        
        let enclosingSym = findEnclosingSymbol(symbols, line);
        if (!enclosingSym && line + 1 < doc.lineCount) {
            enclosingSym = findEnclosingSymbol(symbols, line + 1);
        }
        
        if (!enclosingSym) {
            return `No enclosing class or method symbol found at line ${line + 1}`;
        }
        
        let resultText = "";
        
        // Level 0: Enclosing Context
        resultText += `--- original context ---\n\n`;
        resultText += `File: ${vscode.workspace.asRelativePath(uri)} (Line ${enclosingSym.range.start.line + 1} - ${enclosingSym.range.end.line + 1})\n`;
        resultText += doc.getText(enclosingSym.range) + "\n\n";
        
        // Perform reference tracing for methods, functions, constructors, classes, structs, interfaces, and enums
        const shouldTraceReferences = [
            vscode.SymbolKind.Method,
            vscode.SymbolKind.Function,
            vscode.SymbolKind.Constructor,
            vscode.SymbolKind.Class,
            vscode.SymbolKind.Interface,
            vscode.SymbolKind.Struct,
            vscode.SymbolKind.Enum
        ].includes(enclosingSym.kind);
        
        if (shouldTraceReferences && callStackLevel > 0) {
            const visited = new Set();
            visited.add(`${uri.toString()}:${enclosingSym.name}`);
            
            let currentLevelSymbols = [{
                uri: uri,
                position: enclosingSym.selectionRange.start, // signature position
                name: enclosingSym.name
            }];
            
            for (let level = 1; level <= callStackLevel; level++) {
                resultText += `--- invocation stack level ${level} ---\n\n`;
                let nextLevelSymbols = [];
                let levelOutputs = [];
                
                for (const sym of currentLevelSymbols) {
                    const references = await vscode.commands.executeCommand('vscode.executeReferenceProvider', sym.uri, sym.position) || [];
                    
                    for (const ref of references) {
                        // Skip references that point to the declaration itself
                        const isDecl = ref.uri.toString() === sym.uri.toString() &&
                                       ref.range.start.line === sym.position.line;
                        if (isDecl) {
                            continue;
                        }
                        
                        try {
                            const refDoc = await vscode.workspace.openTextDocument(ref.uri);
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
                                    if (!visited.has(key)) {
                                        visited.add(key);
                                        
                                        const body = refDoc.getText(enclosingCaller.range);
                                        levelOutputs.push(`File: ${vscode.workspace.asRelativePath(ref.uri)} (Line ${enclosingCaller.range.start.line + 1})\n${body}`);
                                        
                                        nextLevelSymbols.push({
                                            uri: ref.uri,
                                            position: enclosingCaller.selectionRange.start,
                                            name: enclosingCaller.name
                                        });
                                    }
                                }
                            }
                        } catch (err) {
                            // Ignore or log error
                        }
                    }
                }
                
                if (levelOutputs.length > 0) {
                    resultText += levelOutputs.join('\n\n') + "\n\n";
                } else {
                    resultText += "(No caller references found at this level)\n\n";
                    break;
                }
                
                currentLevelSymbols = nextLevelSymbols;
            }
        }
        
        return resultText;
    } catch (error) {
        return `Error getting context at location: ${error.message}`;
    }
}

module.exports = {
    getContextAtLocation,
    findEnclosingSymbol
};
