import fs from 'fs';
import path from 'path';
import readline from 'readline';

// Standalone mock of VS Code API for Node.js
const vscode = {
    workspace: {
        workspaceFolders: [{ uri: { fsPath: process.cwd() } }],
        async openTextDocument(uri) {
            const fsPath = typeof uri === 'string' ? uri : uri.fsPath;
            const text = fs.readFileSync(fsPath, 'utf8');
            const lines = text.split(/\r?\n/);
            return {
                fsPath,
                lineCount: lines.length,
                lineAt(lineNum) {
                    return { text: lines[lineNum] || "" };
                },
                getText(range) {
                    if (!range) return text;
                    const startLine = range.start.line;
                    const startChar = range.start.character;
                    const endLine = range.end.line;
                    const endChar = range.end.character;
                    if (startLine === endLine) {
                        return (lines[startLine] || "").substring(startChar, endChar);
                    }
                    let result = (lines[startLine] || "").substring(startChar);
                    for (let i = startLine + 1; i < endLine; i++) {
                        result += '\n' + (lines[i] || "");
                    }
                    result += '\n' + (lines[endLine] || "").substring(0, endChar);
                    return result;
                },
                async save() {
                    return true;
                }
            };
        },
        asRelativePath(uri) {
            const fsPath = typeof uri === 'string' ? uri : uri.fsPath;
            return path.relative(process.cwd(), fsPath).replace(/\\/g, '/');
        },
        getWorkspaceFolder(uri) {
            const fsPath = typeof uri === 'string' ? uri : uri.fsPath;
            const absolutePath = path.resolve(fsPath);
            const root = path.resolve(process.cwd());
            if (absolutePath.startsWith(root)) {
                return { uri: { fsPath: root } };
            }
            return undefined;
        },
        async findFiles(includeGlob, excludeGlob) {
            const results = [];
            const root = process.cwd();
            
            const globToRegex = (pattern) => {
                let escaped = pattern
                    .replace(/[.+^${}()|[\]\\]/g, '\\$&')
                    .replace(/\*\*/g, '.*')
                    .replace(/\*/g, '[^/]*')
                    .replace(/\?/g, '.');
                return new RegExp('^' + escaped + '$', 'i');
            };

            const regex = globToRegex(includeGlob);

            function walk(dir) {
                let list;
                try {
                    list = fs.readdirSync(dir);
                } catch (e) {
                    return;
                }
                for (const file of list) {
                    if (['node_modules', '.git', '.vscode', 'bin', 'obj', 'dist', 'out'].includes(file)) {
                        continue;
                    }
                    const fullPath = path.join(dir, file);
                    let stat;
                    try {
                        stat = fs.statSync(fullPath);
                    } catch (e) {
                        continue;
                    }
                    if (stat.isDirectory()) {
                        walk(fullPath);
                    } else {
                        const relative = path.relative(root, fullPath).replace(/\\/g, '/');
                        if (regex.test(relative) || regex.test(file)) {
                            results.push(vscode.Uri.file(fullPath));
                        }
                    }
                }
            }

            walk(root);
            return results;
        },
        async applyEdit(edit) {
            if (edit && typeof edit._apply === 'function') {
                return edit._apply();
            }
            return false;
        }
    },
    Uri: {
        file(filePath) {
            const resolved = path.resolve(filePath);
            return {
                fsPath: resolved,
                toString() {
                    return 'file:///' + resolved.replace(/\\/g, '/');
                }
            };
        }
    },
    commands: {
        async executeCommand(command, ...args) {
            console.log(`[COMMAND] Executed: ${command} with args:`, args);
            return [];
        }
    },
    languages: {
        getDiagnostics(uri) {
            return [];
        }
    },
    SymbolKind: {
        File: 0, Module: 1, Namespace: 2, Package: 3, Class: 4, Method: 5, Property: 6,
        Field: 7, Constructor: 8, Enum: 9, Interface: 10, Function: 11, Variable: 12,
        Constant: 13, String: 14, Number: 15, Boolean: 16, Array: 17, Object: 18,
        Key: 19, Null: 20, EnumMember: 21, Struct: 22, Event: 23, Operator: 24, TypeParameter: 25
    },
    DiagnosticSeverity: {
        Error: 0, Warning: 1, Information: 2, Hint: 3
    },
    window: {
        activeTextEditor: null,
        async showWarningMessage(message, options, ...items) {
            console.log(`\n[WARNING] ${message}\n`);
            
            const rl = readline.createInterface({
                input: process.stdin,
                output: process.stdout
            });

            return new Promise(resolve => {
                rl.question('Approve this request? (y/N): ', (answer) => {
                    rl.close();
                    if (answer.trim().toLowerCase() === 'y' || answer.trim().toLowerCase() === 'yes') {
                        resolve(items[0]);
                    } else {
                        resolve(items[1]);
                    }
                });
            });
        }
    },
    WorkspaceEdit: class {
        constructor() {
            this._edits = new Map();
        }
        
        replace(uri, range, newText) {
            const fsPath = uri.fsPath;
            if (!this._edits.has(fsPath)) this._edits.set(fsPath, []);
            this._edits.get(fsPath).push({ type: 'replace', range, newText });
        }
        
        insert(uri, position, newText) {
            const fsPath = uri.fsPath;
            if (!this._edits.has(fsPath)) this._edits.set(fsPath, []);
            this._edits.get(fsPath).push({ type: 'insert', position, newText });
        }
        
        delete(uri, range) {
            const fsPath = uri.fsPath;
            if (!this._edits.has(fsPath)) this._edits.set(fsPath, []);
            this._edits.get(fsPath).push({ type: 'delete', range });
        }
        
        entries() {
            const list = [];
            for (const [fsPath, edits] of this._edits.entries()) {
                list.push([{ fsPath }, edits]);
            }
            return list;
        }
        
        _apply() {
            for (const [fsPath, edits] of this._edits.entries()) {
                if (!fs.existsSync(fsPath)) {
                    fs.writeFileSync(fsPath, '', 'utf8');
                }
                let text = fs.readFileSync(fsPath, 'utf8');
                let lines = text.split(/\r?\n/);
                
                const sortedEdits = [...edits].sort((a, b) => {
                    const lineA = a.range ? a.range.start.line : a.position.line;
                    const lineB = b.range ? b.range.start.line : b.position.line;
                    if (lineB !== lineA) return lineB - lineA;
                    const charA = a.range ? a.range.start.character : a.position.character;
                    const charB = b.range ? b.range.start.character : b.position.character;
                    return charB - charA;
                });
                
                for (const edit of sortedEdits) {
                    if (edit.type === 'replace') {
                        const { range, newText } = edit;
                        const startLine = range.start.line;
                        const startChar = range.start.character;
                        const endLine = range.end.line;
                        const endChar = range.end.character;
                        
                        if (startLine === endLine) {
                            lines[startLine] = lines[startLine].substring(0, startChar) + newText + lines[startLine].substring(endChar);
                        } else {
                            const newLines = newText.split(/\r?\n/);
                            const top = lines[startLine].substring(0, startChar);
                            const bottom = lines[endLine].substring(endChar);
                            newLines[0] = top + newLines[0];
                            newLines[newLines.length - 1] = newLines[newLines.length - 1] + bottom;
                            
                            lines.splice(startLine, endLine - startLine + 1, ...newLines);
                        }
                    } else if (edit.type === 'insert') {
                        const { position, newText } = edit;
                        const { line, character } = position;
                        const lineText = lines[line] || "";
                        lines[line] = lineText.substring(0, character) + newText + lineText.substring(character);
                    } else if (edit.type === 'delete') {
                        const { range } = edit;
                        const startLine = range.start.line;
                        const startChar = range.start.character;
                        const endLine = range.end.line;
                        const endChar = range.end.character;
                        
                        if (startLine === endLine) {
                            lines[startLine] = lines[startLine].substring(0, startChar) + lines[startLine].substring(endChar);
                        } else {
                            const top = lines[startLine].substring(0, startChar);
                            const bottom = lines[endLine].substring(endChar);
                            lines.splice(startLine, endLine - startLine + 1, top + bottom);
                        }
                    }
                }
                
                fs.writeFileSync(fsPath, lines.join('\n'), 'utf8');
            }
            return true;
        }
    },
    Position: class {
        constructor(line, character) {
            this.line = line;
            this.character = character;
        }
    },
    Range: class {
        constructor(start, end) {
            this.start = start;
            this.end = end;
        }
    }
};

export default vscode;
