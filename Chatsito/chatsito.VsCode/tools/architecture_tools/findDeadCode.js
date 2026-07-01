const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function findDeadCode(directory) {
    if (!directory) return "Error: Missing directory parameter.";

    try {
        let absPath;
        if (path.isAbsolute(directory)) {
            absPath = directory;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, directory);
            } else {
                return `Error: Could not resolve relative path '${directory}' because no workspace folders are open.`;
            }
        }

        if (!fs.existsSync(absPath)) return `Error: Directory not found at '${absPath}'`;

        const files = await vscode.workspace.findFiles(
            new vscode.RelativePattern(absPath, '**/*.{js,ts}'),
            '**/node_modules/**|**/*.test.js|**/*Tests.js'
        );

        const deadCode = [];

        for (const uri of files) {
            // Ensure doc is open for symbol provider
            await vscode.workspace.openTextDocument(uri);
            const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];
            
            async function processSymbol(sym) {
                if (sym.kind === vscode.SymbolKind.Class || sym.kind === vscode.SymbolKind.Function || sym.kind === vscode.SymbolKind.Method) {
                    if (sym.name !== 'default' && sym.name !== 'module.exports' && sym.name !== 'exports' && sym.name !== 'constructor') {
                        const refs = await vscode.commands.executeCommand('vscode.executeReferenceProvider', uri, sym.selectionRange.start) || [];
                        if (refs.length <= 1) {
                            deadCode.push({
                                name: sym.name,
                                file: vscode.workspace.asRelativePath(uri),
                                line: sym.range.start.line + 1
                            });
                        }
                    }
                }
                if (sym.children && sym.children.length > 0) {
                    for (const child of sym.children) {
                        await processSymbol(child);
                    }
                }
            }

            for (const sym of symbols) {
                await processSymbol(sym);
            }
        }

        if (deadCode.length === 0) {
            return `=== Dead Code Analysis ===\n\nNo dead code found in ${vscode.workspace.asRelativePath(absPath)}`;
        }

        let output = `=== Dead Code Found (${deadCode.length}) ===\n\n`;
        for (const dead of deadCode) {
            output += `  - ${dead.name} at ${dead.file}:${dead.line}\n`;
        }

        return output;
    } catch (e) {
        return `Error finding dead code: ${e.message}`;
    }
}

module.exports = findDeadCode;
