const vscode = require('vscode');
const path = require('path');
const logger = require('./logger');

class PatchManager {
    constructor() {
        this.patchHistory = [];
        this.toolsMap = new Map();
        
        // Lazy load the tools to avoid circular dependencies if needed
        this._loadTools();
    }

    _loadTools() {
        const ToolDefinitionProvider = require('./ToolDefinitionProvider');
        const tools = ToolDefinitionProvider.getTools();
        for (const def of tools) {
            if (def.isPatchingTool) {
                const camelCaseName = def.name.replace(/_([a-z])/g, (m, p1) => p1.toUpperCase());
                const implementationPath = './tools/code_modification/' + camelCaseName;
                this.toolsMap.set(def.name, require(implementationPath));
            }
        }
    }

    resolvePath(filePath) {
        const PathResolver = require('./PathResolver');
        return vscode.Uri.file(PathResolver.resolveAndValidateWorkspacePath(filePath));
    }

    /**
     * Helper to generate a simple diff or change summary.
     */
    generateDiff(editDescription, edit) {
        const entriesCount = typeof edit.entries === 'function' ? edit.entries().length : 0;
        let diffText = `[Diff Summary] ${editDescription}: ${entriesCount} file(s) modified.`;
        if (entriesCount > 0) {
            const uris = edit.entries().map(entry => vscode.workspace.asRelativePath(entry[0]));
            diffText += `\nFiles affected:\n- ` + uris.join('\n- ');
        }
        return diffText;
    }



    /**
     * Helper to log changes to history
     */
    trackChange(description, editOrCommand) {
        let count = 0;
        if (editOrCommand && typeof editOrCommand.entries === 'function') {
            count = editOrCommand.entries().length;
        }
        
        this.patchHistory.push({
            timestamp: new Date().toISOString(),
            description: description,
            filesAffected: count
        });
        logger.log(`[PatchManager] Tracked change: ${description}`);
    }

    /**
     * Entry point for LLM callbacks to execute code modification tools.
     */
    async executeTool(toolName, args, selectedMode) {
        const toolFn = this.toolsMap.get(toolName);
        if (!toolFn) {
            return `Error: Unknown patch tool '${toolName}'`;
        }

        // Stale edit check for specific tools (like replace_code)
        if (args.expected_original_text && args.file_path && args.start_line !== undefined && args.start_char !== undefined && args.end_line !== undefined && args.end_char !== undefined) {
            
            // Prevent LLM hallucination where it copies the original text into the replacement field
            if (args.text_to_replace) {
                const normalizedToReplace = args.text_to_replace.replace(/\r\n/g, '\n').trim();
                const normalizedExpectedStr = args.expected_original_text.replace(/\r\n/g, '\n').trim();
                if (normalizedToReplace === normalizedExpectedStr) {
                    return `Error: 'text_to_replace' is identical to 'expected_original_text'. You must provide the NEW modified code in 'text_to_replace'. The replacement was rejected because it would result in no changes.`;
                }
            }

            try {
                let resolvedUri;
                try {
                    resolvedUri = this.resolvePath(args.file_path);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
                
                const doc = await vscode.workspace.openTextDocument(resolvedUri);
                const range = new vscode.Range(new vscode.Position(parseInt(args.start_line, 10) - 1, parseInt(args.start_char, 10) - 1), new vscode.Position(parseInt(args.end_line, 10) - 1, parseInt(args.end_char, 10) - 1));
                const currentText = doc.getText(range);
                
                const normalizedCurrent = currentText.replace(/\r\n/g, '\n');
                const normalizedExpected = args.expected_original_text.replace(/\r\n/g, '\n');
                
                if (normalizedCurrent !== normalizedExpected) {
                    const fullText = doc.getText().replace(/\r\n/g, '\n');
                    const index = fullText.indexOf(normalizedExpected);
                    const lastIndex = fullText.lastIndexOf(normalizedExpected);
                    
                    if (index !== -1 && index === lastIndex) {
                        const before = fullText.substring(0, index);
                        const linesBefore = before.split('\n');
                        const newStartLine = linesBefore.length;
                        const newStartChar = linesBefore[linesBefore.length - 1].length + 1;
                        
                        const expectedLines = normalizedExpected.split('\n');
                        const newEndLine = newStartLine + expectedLines.length - 1;
                        const newEndChar = expectedLines.length > 1 
                            ? expectedLines[expectedLines.length - 1].length + 1 
                            : newStartChar + normalizedExpected.length;
                        
                        args.start_line = newStartLine;
                        args.start_char = newStartChar;
                        args.end_line = newEndLine;
                        args.end_char = newEndChar;
                        
                        logger.log(`[PatchManager] Auto-corrected tool range to line ${newStartLine}:${newStartChar} -> ${newEndLine}:${newEndChar}`);
                    } else {
                        return `Error: Stale edit detected in ${vscode.workspace.asRelativePath(resolvedUri)}. The text at the specified range has changed. Expected: "${args.expected_original_text}", Found: "${currentText}". Please refresh your context and try again.`;
                    }
                }
            } catch (e) {
                return `Error verifying target file for stale edit: ${e.message}`;
            }
        }

        try {
            const ToolDefinitionProvider = require('./ToolDefinitionProvider');
            const def = ToolDefinitionProvider.getToolDefinition(toolName);
            if (!def || !def.adapter) {
                return `Error: Tool '${toolName}' does not have a valid adapter defined.`;
            }

            let result = await def.adapter(args, toolFn);

            if (typeof result === 'string') {
                return result;
            }
            
            if (result && result.error) {
                return result.error;
            }
            
            if (!result || (!result.edit && !result.command)) {
                return `Error: Tool '${toolName}' did not return a valid WorkspaceEdit or command.`;
            }

            if (result.edit) {
                const edit = result.edit;
                const diffSummary = this.generateDiff(toolName, edit);
                
                // Show diff before applying
                let isApproved = false;
                if (selectedMode === 'ai' || process.env.NODE_ENV === 'test' || process.env.VSCODE_IPC_HOOK_EXTHOST) {
                    isApproved = true;
                } else {
                    try {
                        const message = `Chatsito wants to apply a patch:\n\n${diffSummary}\n\nDo you want to apply these changes?`;
                        const selection = await vscode.window.showWarningMessage(
                            message,
                            { modal: true },
                            'Apply Patch',
                            'Reject'
                        );
                        isApproved = (selection === 'Apply Patch');
                    } catch (err) {
                        // In VS Code test environment, dialogs might throw an error. Fallback to true for tests.
                        if (err.message && err.message.includes('refused to show dialog in tests')) {
                            isApproved = true;
                        } else {
                            throw err;
                        }
                    }
                }

                if (!isApproved) {
                    return `Execution cancelled: User denied permission to apply patch for ${toolName}.`;
                }

                const entriesCount = typeof edit.entries === 'function' ? edit.entries().length : 0;
                const success = await vscode.workspace.applyEdit(edit);
                
                if (success) {
                    this.trackChange(toolName, edit);

                    // Save all affected documents
                    if (typeof edit.entries === 'function') {
                        const uris = edit.entries().map(entry => entry[0]);
                        for (const uri of uris) {
                            try {
                                const doc = await vscode.workspace.openTextDocument(uri);
                                await doc.save();
                            } catch (e) {
                                logger.log(`[PatchManager] Warning: Failed to save document ${uri.fsPath}`);
                            }
                        }
                    }
                    
                    return `${result.successMessage || 'Successfully applied modification.'}\n${diffSummary}`;
                } else {
                    return `Failed to apply workspace edit for: ${toolName}. Possible merge conflict or overlapping edits.`;
                }
            } else if (result.command) {
                await vscode.commands.executeCommand(result.command, ...(result.args || []));
                this.trackChange(toolName, { command: result.command });
                return result.successMessage || `Executed command for ${toolName}.`;
            }
            
        } catch (e) {
            return `Error executing patch tool ${toolName}: ${e.message}`;
        }
    }
}

module.exports = new PatchManager();
