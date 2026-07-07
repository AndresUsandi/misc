import path from 'path';
import vscode from './vscode.js';
import { logger } from './logger.js';
import ToolDefinitionProvider from './ToolDefinitionProvider.js';

class PatchManager {
    constructor() {
        this.patchHistory = [];
        this.toolsMap = new Map();
        this._loadTools();
    }

    async _loadTools() {
        const tools = ToolDefinitionProvider.getTools();
        for (const def of tools) {
            if (def.isPatchingTool) {
                const implementationPath = './tools/code_modification/' + def.name + '.js';
                // Dynamic import for patching tools implementation
                const rawImpl = (await import(implementationPath)).default;
                this.toolsMap.set(def.name, rawImpl);
            }
        }
    }

    resolvePath(filePath) {
        // Resolve absolute or workspace-relative path safely
        const resolved = path.isAbsolute(filePath) ? filePath : path.resolve(process.cwd(), filePath);
        return vscode.Uri.file(resolved);
    }

    generateDiff(editDescription, edit) {
        const entriesCount = typeof edit.entries === 'function' ? edit.entries().length : 0;
        let diffText = `[Diff Summary] ${editDescription}: ${entriesCount} file(s) modified.`;
        if (entriesCount > 0) {
            const uris = edit.entries().map(entry => vscode.workspace.asRelativePath(entry[0].fsPath || entry[0]));
            diffText += `\nFiles affected:\n- ` + uris.join('\n- ');
        }
        return diffText;
    }

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

    async executeTool(toolName, args, selectedMode) {
        let toolFn = this.toolsMap.get(toolName);
        if (!toolFn) {
            // Lazy load if not initialized
            try {
                const implementationPath = './tools/code_modification/' + toolName + '.js';
                const rawImpl = (await import(implementationPath)).default;
                this.toolsMap.set(toolName, rawImpl);
                toolFn = rawImpl;
            } catch (e) {
                return `Error: Unknown patch tool '${toolName}'`;
            }
        }

        try {
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

                let isApproved = false;
                if (selectedMode === 'ai' || process.env.NODE_ENV === 'test') {
                    isApproved = true;
                } else if (selectedMode === 'hybrid') {
                    if (typeof edit.entries === 'function') {
                        const uris = edit.entries().map(entry => entry[0]);
                        isApproved = uris.every(uri => vscode.workspace.getWorkspaceFolder(uri) !== undefined);
                    }
                }

                if (!isApproved) {
                    try {
                        const message = `Fixito wants to apply a patch:\n\n${diffSummary}\n\nDo you want to apply these changes?`;
                        const selection = await vscode.window.showWarningMessage(
                            message,
                            { modal: true },
                            'Apply Patch',
                            'Reject'
                        );
                        isApproved = (selection === 'Apply Patch');
                    } catch (err) {
                        isApproved = false;
                    }
                }

                if (!isApproved) {
                    return `Execution cancelled: User denied permission to apply patch for ${toolName}.`;
                }

                const success = await vscode.workspace.applyEdit(edit);

                if (success) {
                    this.trackChange(toolName, edit);

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

export default new PatchManager();
