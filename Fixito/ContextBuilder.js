import fs from 'fs';
import path from 'path';
import cp from 'child_process';
import vscode from './vscode.js';

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

async function getInitialCallerContext(filePath, lineNumber, callStackLevel = 2) {
    const line = lineNumber - 1; // 1-based to 0-based

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
        const doc = await vscode.workspace.openTextDocument(uri);
        const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];

        const enclosingSym = findEnclosingSymbol(symbols, line);
        if (!enclosingSym) {
            return "";
        }

        const shouldTraceReferences = [
            vscode.SymbolKind.Method,
            vscode.SymbolKind.Function,
            vscode.SymbolKind.Constructor,
            vscode.SymbolKind.Class,
            vscode.SymbolKind.Interface,
            vscode.SymbolKind.Struct,
            vscode.SymbolKind.Enum
        ].includes(enclosingSym.kind);

        if (!shouldTraceReferences) {
            return "";
        }

        let resultText = "";

        resultText += `--- original context ---\n\n`;
        resultText += `File: ${vscode.workspace.asRelativePath(uri)} (Line ${enclosingSym.range.start.line + 1} - ${enclosingSym.range.end.line + 1})\n`;
        resultText += doc.getText(enclosingSym.range) + "\n\n";

        if (callStackLevel > 0) {
            const visited = new Set();
            visited.add(`${uri.toString()}:${enclosingSym.name}`);

            let currentLevelSymbols = [{
                uri: uri,
                position: enclosingSym.selectionRange.start,
                name: enclosingSym.name
            }];

            for (let level = 1; level <= callStackLevel; level++) {
                resultText += `--- invocation stack level ${level} ---\n\n`;
                let nextLevelSymbols = [];
                let levelOutputs = [];

                for (const sym of currentLevelSymbols) {
                    const references = await vscode.commands.executeCommand('vscode.executeReferenceProvider', sym.uri, sym.position) || [];

                    for (const ref of references) {
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
                            console.error(err);
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
    } catch (err) {
        return `Failed to open or resolve context for ${filePath}: ${err.message}`;
    }
}

async function getInitialCalleeContext(filePath, lineNumber, callStackLevel = 2) {
    const line = lineNumber - 1; // 1-based to 0-based

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
            return "";
        }

        const shouldTrace = [
            vscode.SymbolKind.Method,
            vscode.SymbolKind.Function,
            vscode.SymbolKind.Constructor,
            vscode.SymbolKind.Class,
            vscode.SymbolKind.Interface,
            vscode.SymbolKind.Struct,
            vscode.SymbolKind.Enum
        ].includes(enclosingSym.kind);

        if (!shouldTrace) {
            return "";
        }

        let callHierarchyItems = [];
        try {
            callHierarchyItems = await vscode.commands.executeCommand('vscode.executePrepareCallHierarchy', uri, enclosingSym.selectionRange.start) || [];
        } catch (e) {
            callHierarchyItems = [];
        }

        if (callHierarchyItems.length === 0) {
            return "";
        }

        let resultText = "";
        const visited = new Set();

        let currentLevelItems = callHierarchyItems;
        for (const item of currentLevelItems) {
            visited.add(item.uri.toString() + ":" + item.range.start.line + ":" + item.range.start.character);
        }

        for (let level = 1; level <= callStackLevel; level++) {
            resultText += `--- callee stack level ${level} ---\n\n`;
            let nextLevelItems = [];
            let levelOutputs = [];

            for (const item of currentLevelItems) {
                const outgoingCalls = await vscode.commands.executeCommand('vscode.executeProvideOutgoingCalls', item) || [];

                for (const call of outgoingCalls) {
                    const callee = call.to;

                    const isInsideWorkspace = vscode.workspace.getWorkspaceFolder(callee.uri) !== undefined;
                    if (!isInsideWorkspace) {
                        continue;
                    }

                    const key = callee.uri.toString() + ":" + callee.range.start.line + ":" + callee.range.start.character;
                    if (!visited.has(key)) {
                        visited.add(key);

                        try {
                            const calleeDoc = await vscode.workspace.openTextDocument(callee.uri);
                            const body = calleeDoc.getText(callee.range);
                            const relativePath = vscode.workspace.asRelativePath(callee.uri);
                            levelOutputs.push(`File: ${relativePath} (Line ${callee.range.start.line + 1})\nSymbol: ${callee.name}\n${body}`);

                            nextLevelItems.push(callee);
                        } catch (err) {
                            console.error(`Failed to read callee document: ${callee.uri.toString()}`, err);
                        }
                    }
                }
            }

            if (levelOutputs.length > 0) {
                resultText += levelOutputs.join('\n\n') + "\n\n";
            } else {
                resultText += "(No callee functions found at this level)\n\n";
                break;
            }

            currentLevelItems = nextLevelItems;
        }

        return resultText;
    } catch (err) {
        return `Failed to resolve callee context for ${filePath}: ${err.message}`;
    }
}

function extractImportTargets(fileContent) {
    const targets = new Set();

    const quotedRegexes = [
        /import\s+.*?\s+from\s+['"]([^'"]+)['"]/g,
        /require\(\s*['"]([^'"]+)['"]\s*\)/g,
        /#include\s+["<]([^">]+)[">]/g,
        /import\s+['"]([^'"]+)['"]/g,
        /from\s+['"]([^'"]+)['"]\s+import/g
    ];

    for (const regex of quotedRegexes) {
        let match;
        regex.lastIndex = 0;
        while ((match = regex.exec(fileContent)) !== null) {
            targets.add(match[1].trim());
        }
    }

    const wordRegexes = [
        /using\s+([\w.]+)\s*;/g,
        /import\s+([\w.]+)\s*;/g,
        /from\s+([\w.]+)\s+import/g
    ];

    for (const regex of wordRegexes) {
        let match;
        regex.lastIndex = 0;
        while ((match = regex.exec(fileContent)) !== null) {
            targets.add(match[1].trim());
        }
    }

    const pythonImportRegex = /^\s*import\s+([\w.,\s]+)/gm;
    let match;
    pythonImportRegex.lastIndex = 0;
    while ((match = pythonImportRegex.exec(fileContent)) !== null) {
        const parts = match[1].split(',');
        for (const p of parts) {
            const cleanPart = p.trim().split(/\s+/)[0];
            if (cleanPart) targets.add(cleanPart);
        }
    }

    return Array.from(targets);
}

async function resolveTargetToUris(target, currentFilePath, workspaceFolders) {
    const results = [];
    if (!target) return results;

    const currentDir = path.dirname(currentFilePath);
    const workspaceRoot = workspaceFolders?.[0]?.uri.fsPath;

    if (target.startsWith('.')) {
        const resolvedPath = path.resolve(currentDir, target);
        if (fs.existsSync(resolvedPath) && fs.statSync(resolvedPath).isFile()) {
            results.push(vscode.Uri.file(resolvedPath));
            return results;
        }

        const extList = ['.js', '.ts', '.jsx', '.tsx', '.py', '.cs', '.java', '.h', '.cpp', '.json'];
        for (const ext of extList) {
            const pathWithExt = resolvedPath + ext;
            if (fs.existsSync(pathWithExt) && fs.statSync(pathWithExt).isFile()) {
                results.push(vscode.Uri.file(pathWithExt));
                return results;
            }
        }

        const baseName = path.basename(resolvedPath);
        const relativeDir = path.relative(workspaceRoot || currentDir, path.dirname(resolvedPath));
        const glob = relativeDir ? `${relativeDir}/${baseName}.*` : `${baseName}.*`;
        const found = await vscode.workspace.findFiles(glob, '**/node_modules/**');
        if (found.length > 0) {
            return found;
        }
    } else {
        const dottedPath = target.replace(/\./g, '/');

        if (workspaceRoot) {
            const fullWorkspacePath = path.resolve(workspaceRoot, dottedPath);
            if (fs.existsSync(fullWorkspacePath) && fs.statSync(fullWorkspacePath).isFile()) {
                results.push(vscode.Uri.file(fullWorkspacePath));
                return results;
            }
            const extList = ['.js', '.ts', '.py', '.cs', '.java', '.h', '.cpp'];
            for (const ext of extList) {
                const pathWithExt = fullWorkspacePath + ext;
                if (fs.existsSync(pathWithExt) && fs.statSync(pathWithExt).isFile()) {
                    results.push(vscode.Uri.file(pathWithExt));
                    return results;
                }
            }
        }

        const segments = target.split('.');
        const lastSegment = segments[segments.length - 1];
        if (lastSegment && lastSegment.length > 1) {
            const found = await vscode.workspace.findFiles(`**/${lastSegment}.*`, '**/node_modules/**');
            if (found.length > 0) {
                const matched = found.filter(uri => {
                    const normalized = uri.fsPath.replace(/\\/g, '/');
                    return normalized.includes(dottedPath);
                });
                if (matched.length > 0) {
                    return matched;
                }
                return found;
            }

            try {
                const symbols = await vscode.commands.executeCommand('vscode.executeWorkspaceSymbolProvider', lastSegment) || [];
                const foundUris = symbols
                    .filter(sym => sym.name === lastSegment && sym.location)
                    .map(sym => sym.location.uri);
                if (foundUris.length > 0) {
                    return foundUris;
                }
            } catch (err) {
                // ignore
            }
        }
    }

    return results;
}

async function getInitialFilePathContext(filePath, callStackLevel = 2) {
    const visited = new Set();
    const workspaceFolders = vscode.workspace.workspaceFolders;
    let resultText = "";

    try {
        if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
            const content = fs.readFileSync(filePath, 'utf8');
            const eol = content.includes('\r\n') ? 'CRLF (\\r\\n)' : 'LF (\\n)';
            resultText += `File: ${vscode.workspace.asRelativePath(vscode.Uri.file(filePath))} [Line Endings: ${eol}]\n\n`;
        }
    } catch (e) {
        console.error("Error reading active file format in getInitialFilePathContext:", e);
    }

    let currentLevelPaths = [filePath];
    visited.add(path.normalize(filePath));

    for (let level = 1; level <= callStackLevel; level++) {
        let nextLevelPaths = [];
        let levelOutputs = [];

        for (const currentPath of currentLevelPaths) {
            try {
                if (!fs.existsSync(currentPath)) continue;
                if (!fs.statSync(currentPath).isFile()) continue;
                const content = fs.readFileSync(currentPath, 'utf8');
                const targets = extractImportTargets(content);

                for (const target of targets) {
                    const resolvedUris = await resolveTargetToUris(target, currentPath, workspaceFolders);
                    for (const uri of resolvedUris) {
                        const fsPath = path.normalize(uri.fsPath);
                        if (!visited.has(fsPath)) {
                            visited.add(fsPath);
                            nextLevelPaths.push(fsPath);

                            const relativePath = vscode.workspace.asRelativePath(uri);
                            try {
                                const fileContent = fs.readFileSync(fsPath, 'utf8');
                                const eol = fileContent.includes('\r\n') ? 'CRLF (\\r\\n)' : 'LF (\\n)';
                                levelOutputs.push(`File: ${relativePath} [Line Endings: ${eol}]\n${fileContent}`);
                            } catch (e) {
                                levelOutputs.push(`File: ${relativePath} (Error reading file: ${e.message})`);
                            }
                        }
                    }
                }
            } catch (err) {
                console.error(`Error processing imports for ${currentPath}:`, err);
            }
        }

        if (levelOutputs.length > 0) {
            resultText += `--- import stack level ${level} ---\n\n`;
            resultText += levelOutputs.join('\n\n') + "\n\n";
        } else {
            break;
        }

        currentLevelPaths = nextLevelPaths;
    }

    return resultText;
}

function getSurroundingCodeContext(doc, uri, lineNumber) {
    const totalLines = doc.lineCount;
    const cursorLine = lineNumber - 1;
    
    const startLine = Math.max(0, cursorLine - 50);
    const endLine = Math.min(totalLines - 1, cursorLine + 50);
    
    let result = `--- original context ---\n\n`;
    result += `File: ${vscode.workspace.asRelativePath(uri)} (Line ${startLine + 1} - ${endLine + 1})\n`;
    
    for (let i = startLine; i <= endLine; i++) {
        result += doc.lineAt(i).text + "\n";
    }
    return result + "\n";
}

async function getInitialDiagnosticsContext(filePath, lineNumber) {
    let uri;
    if (path.isAbsolute(filePath)) {
        uri = vscode.Uri.file(filePath);
    } else {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) return "";
        uri = vscode.Uri.file(path.join(workspaceFolder.uri.fsPath, filePath));
    }

    try {
        const diagnostics = vscode.languages.getDiagnostics(uri) || [];
        const cursorLine = lineNumber - 1;
        
        const nearDiagnostics = diagnostics.filter(diag => {
            return Math.abs(diag.range.start.line - cursorLine) <= 10;
        });

        if (nearDiagnostics.length === 0) return "";

        let result = "";
        for (const diag of nearDiagnostics) {
            const severityStr = vscode.DiagnosticSeverity[diag.severity] || "Diagnostic";
            result += `[${severityStr}] Line ${diag.range.start.line + 1}, Char ${diag.range.start.character + 1}: ${diag.message}\n`;
        }
        return result + "\n";
    } catch (e) {
        return "";
    }
}

async function getInitialSelectedTextContext() {
    try {
        const editor = vscode.window.activeTextEditor;
        if (editor && !editor.selection.isEmpty) {
            const selectedText = editor.document.getText(editor.selection);
            return selectedText + "\n\n";
        }
    } catch (e) {
        // ignore
    }
    return "";
}

function findEnclosingClassSymbol(symbols, line) {
    for (const sym of symbols) {
        if (sym.range.start.line <= line && sym.range.end.line >= line) {
            if (sym.kind === vscode.SymbolKind.Class || sym.kind === vscode.SymbolKind.Interface || sym.kind === vscode.SymbolKind.Struct) {
                return sym;
            }
            if (sym.children && sym.children.length > 0) {
                const child = findEnclosingClassSymbol(sym.children, line);
                if (child) return child;
            }
        }
    }
    return null;
}

async function getInitialTypeContext(filePath, lineNumber) {
    const line = lineNumber - 1;
    let uri;
    if (path.isAbsolute(filePath)) {
        uri = vscode.Uri.file(filePath);
    } else {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) return "";
        uri = vscode.Uri.file(path.join(workspaceFolder.uri.fsPath, filePath));
    }

    try {
        const doc = await vscode.workspace.openTextDocument(uri);
        const symbols = await vscode.commands.executeCommand('vscode.executeDocumentSymbolProvider', uri) || [];
        const classSym = findEnclosingClassSymbol(symbols, line);
        if (!classSym) return "";

        let result = `Class Name: ${classSym.name}\n`;
        
        const children = classSym.children || [];
        const constructors = children.filter(c => c.kind === vscode.SymbolKind.Constructor);
        
        let dependencies = [];
        for (const c of constructors) {
            const signatureLine = doc.lineAt(c.selectionRange.start.line).text;
            const openParen = signatureLine.indexOf('(');
            const closeParen = signatureLine.indexOf(')', openParen);
            if (openParen !== -1 && closeParen !== -1) {
                const params = signatureLine.substring(openParen + 1, closeParen).trim();
                if (params) {
                    dependencies.push(params);
                }
            }
        }
        if (dependencies.length > 0) {
            result += `Injected Dependencies: ${dependencies.join('; ')}\n`;
        }

        if (constructors.length > 0) {
            result += `\nConstructors:\n`;
            for (const c of constructors) {
                result += doc.getText(c.range) + "\n\n";
            }
        }

        const fieldsProps = children.filter(c => 
            c.kind === vscode.SymbolKind.Field || 
            c.kind === vscode.SymbolKind.Property ||
            c.kind === vscode.SymbolKind.Variable
        );
        if (fieldsProps.length > 0) {
            result += `Fields & Properties:\n`;
            for (const fp of fieldsProps) {
                result += `- ${fp.name}\n`;
            }
            result += "\n";
        }

        const methods = children.filter(c => 
            c.kind === vscode.SymbolKind.Method || 
            c.kind === vscode.SymbolKind.Function
        );
        if (methods.length > 0) {
            result += `Methods:\n`;
            for (const m of methods) {
                const sigLine = doc.lineAt(m.selectionRange.start.line).text.trim();
                result += `- ${sigLine}\n`;
            }
            result += "\n";
        }

        return result;
    } catch (e) {
        return "";
    }
}

async function getInitialTestsContext(filePath) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) return "";
    
    const ext = path.extname(filePath);
    const baseName = path.basename(filePath, ext);
    if (!baseName) return "";

    try {
        const globs = [
            `**/*${baseName}*test*.*`,
            `**/*${baseName}*Tests*.*`,
            `**/*test*${baseName}*.*`,
            `**/*${baseName}*spec*.*`
        ];
        
        const foundUrisMap = new Map();
        for (const glob of globs) {
            const found = await vscode.workspace.findFiles(glob, '**/node_modules/**');
            for (const uri of found) {
                foundUrisMap.set(uri.toString(), uri);
            }
        }

        const foundUris = Array.from(foundUrisMap.values());
        if (foundUris.length === 0) return "";

        let result = "";
        for (const uri of foundUris) {
            const relPath = vscode.workspace.asRelativePath(uri);
            try {
                const content = fs.readFileSync(uri.fsPath, 'utf8');
                result += `File: ${relPath}\n${content}\n\n`;
            } catch (e) {
                // ignore
            }
        }
        return result;
    } catch (e) {
        return "";
    }
}

async function getInitialGitDiffContext(filePath) {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
    if (!workspaceFolder) return "";
    const workspaceRoot = workspaceFolder.uri.fsPath;

    return new Promise((resolve) => {
        cp.exec(`git diff HEAD -- "${filePath}"`, {
            cwd: workspaceRoot,
            timeout: 4000
        }, (err, stdout) => {
            if (!err && stdout && stdout.trim()) {
                resolve(stdout + "\n\n");
                return;
            }
            
            cp.exec(`git diff -- "${filePath}"`, {
                cwd: workspaceRoot,
                timeout: 4000
            }, (err2, stdout2) => {
                if (!err2 && stdout2 && stdout2.trim()) {
                    resolve(stdout2 + "\n\n");
                } else {
                    resolve("");
                }
            });
        });
    });
}

async function getInitialProjectContext(filePath) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) return "";
    const workspaceRoot = workspaceFolders[0].uri.fsPath;

    const projectFileNames = [
        'package.json',
        'pyproject.toml',
        'requirements.txt',
        'tsconfig.json',
        'gemfile',
        'cargo.toml',
        'build.gradle',
        'pom.xml'
    ];

    let currentDir = path.dirname(filePath);
    const foundFiles = [];

    while (true) {
        try {
            const filesInDir = fs.readdirSync(currentDir);
            for (const f of filesInDir) {
                const lowerF = f.toLowerCase();
                const matches = projectFileNames.includes(lowerF) || f.endsWith('.csproj');
                if (matches) {
                    const fullPath = path.join(currentDir, f);
                    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isFile()) {
                        foundFiles.push(fullPath);
                    }
                }
            }
        } catch (e) {
            // ignore
        }

        if (currentDir === workspaceRoot || currentDir === path.dirname(currentDir)) {
            break;
        }
        currentDir = path.dirname(currentDir);
    }

    if (foundFiles.length === 0) return "";

    let result = "";
    const uniquePaths = Array.from(new Set(foundFiles));
    for (const f of uniquePaths) {
        const relPath = vscode.workspace.asRelativePath(vscode.Uri.file(f));
        try {
            const content = fs.readFileSync(f, 'utf8');
            result += `File: ${relPath}\n${content}\n\n`;
        } catch (e) {
            // ignore
        }
    }
    return result;
}

function buildDirTree(dirPath, currentLevel, maxLevel, workspaceRoot) {
    if (currentLevel > maxLevel) return "";
    let output = "";
    try {
        const files = fs.readdirSync(dirPath);
        const indent = "  ".repeat(currentLevel - 1);
        
        for (const file of files) {
            if (['node_modules', '.git', '.vscode', 'bin', 'obj', 'dist', 'out', '.vscode-test'].includes(file)) {
                continue;
            }
            const fullPath = path.join(dirPath, file);
            const stat = fs.statSync(fullPath);
            if (stat.isDirectory()) {
                output += `${indent}[Dir] ${file}\n`;
                output += buildDirTree(fullPath, currentLevel + 1, maxLevel, workspaceRoot);
            } else {
                output += `${indent}${file}\n`;
            }
        }
    } catch (err) {
        // ignore
    }
    return output;
}

async function getInitialWorkspaceContext(filePath, callStackLevel = 2) {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders) return "";
    const workspaceRoot = workspaceFolders[0].uri.fsPath;
    
    try {
        let result = `Root Folder: ${path.basename(workspaceRoot)}\n`;
        result += buildDirTree(workspaceRoot, 1, callStackLevel, workspaceRoot);
        return result + "\n";
    } catch (e) {
        return "";
    }
}

async function getInitialPromptContext(filePath, lineNumber, callStackLevel = 2) {
    if (!filePath) {
        return "Failed to open or resolve context for: empty file path.";
    }
    let absolutePath = filePath;
    if (!path.isAbsolute(filePath)) {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            absolutePath = path.join(workspaceFolder.uri.fsPath, filePath);
        }
    }

    try {
        if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
            return "";
        }
    } catch (e) {
        return "";
    }

    let callerContext = "";
    let calleeContext = "";
    try {
        callerContext = await getInitialCallerContext(absolutePath, lineNumber, callStackLevel);
        calleeContext = await getInitialCalleeContext(absolutePath, lineNumber, callStackLevel);
    } catch (e) {
        // ignore
    }
    
    const fileContext = await getInitialFilePathContext(absolutePath, callStackLevel);

    if (!callerContext) {
        try {
            const uri = vscode.Uri.file(absolutePath);
            if (fs.existsSync(absolutePath) && fs.statSync(absolutePath).isFile()) {
                const doc = await vscode.workspace.openTextDocument(uri);
                callerContext = getSurroundingCodeContext(doc, uri, lineNumber);
            }
        } catch (e) {
            // ignore
        }
        calleeContext = "";
    }

    const diagnosticsContext = await getInitialDiagnosticsContext(absolutePath, lineNumber);
    const selectedTextContext = await getInitialSelectedTextContext();
    const typeContext = await getInitialTypeContext(absolutePath, lineNumber);
    const testsContext = await getInitialTestsContext(absolutePath);
    const gitDiffContext = await getInitialGitDiffContext(absolutePath);
    const projectContext = await getInitialProjectContext(absolutePath);
    const workspaceContext = await getInitialWorkspaceContext(absolutePath, callStackLevel);

    let combined = "";
    
    if (callerContext) {
        combined += `=== THE FOLLOWING CONTEXT PROVIDES CODE FOR THE CURRENTLY SELECTED FUNCTION OR CLASS AND THEIR REFERENCES (RECURSIVELY) ===\n\n` + callerContext;
    }
    if (calleeContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES CODE FOR THE CURRENTLY SELECTED FUNCTION AND THE FUNCTIONS IT CALLS (RECURSIVELY) ===\n\n` + calleeContext;
    }
    if (fileContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES FILE PATH FOR THE CURRENTLY SELECTED FILE AND ALL IMPORTED FILES (RECURSIVELY) ===\n\n` + fileContext;
    }
    if (diagnosticsContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES DIAGNOSTICS (COMPILER/LINTER ERRORS) NEAR THE CURRENT LOCATION ===\n\n` + diagnosticsContext;
    }
    if (selectedTextContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES THE CURRENTLY SELECTED TEXT IN THE EDITOR ===\n\n` + selectedTextContext;
    }
    if (typeContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES A SUMMARY OF THE CURRENT TYPE/CLASS ===\n\n` + typeContext;
    }
    if (testsContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES RELATED TESTS ===\n\n` + testsContext;
    }
    if (gitDiffContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES THE GIT DIFF FOR THE CURRENT FILE ===\n\n` + gitDiffContext;
    }
    if (projectContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES THE PROJECT CONFIGURATION FILES ===\n\n` + projectContext;
    }
    if (workspaceContext) {
        if (combined) combined += "\n";
        combined += `=== THE FOLLOWING CONTEXT PROVIDES THE WORKSPACE STRUCTURE SUMMARY ===\n\n` + workspaceContext;
    }

    return combined;
}

export default getInitialPromptContext;
