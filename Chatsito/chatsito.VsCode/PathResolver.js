const vscode = require('vscode');
const path = require('path');

class PathResolver {
    /**
     * Resolves a file path and strictly validates that it falls within the current workspace.
     * @param {string} filePath - The absolute or relative path to resolve.
     * @returns {string} The resolved absolute path if valid.
     * @throws {Error} If the path is outside the workspace or no workspace is open.
     */
    static resolveAndValidateWorkspacePath(filePath) {
        if (!filePath || filePath.trim() === '') {
            throw new Error("No path provided.");
        }

        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            throw new Error("No workspace folders are open.");
        }

        const workspaceRoot = workspaceFolders[0].uri.fsPath;
        let resolvedPath;

        if (path.isAbsolute(filePath)) {
            resolvedPath = filePath;
        } else {
            resolvedPath = path.resolve(workspaceRoot, filePath);
        }

        // Normalize paths for comparison to avoid bypasses using '..'
        // Adding path.sep to ensure we match whole directories (e.g., /workspace-a doesn't match /workspace)
        let normalizedResolvedPath = path.normalize(resolvedPath).toLowerCase();
        let normalizedWorkspaceRoot = path.normalize(workspaceRoot).toLowerCase();

        if (!normalizedWorkspaceRoot.endsWith(path.sep)) {
            normalizedWorkspaceRoot += path.sep;
        }
        
        // If the path is exactly the workspace root, that's fine too
        if (normalizedResolvedPath === normalizedWorkspaceRoot.slice(0, -1)) {
            return resolvedPath;
        }

        if (!normalizedResolvedPath.startsWith(normalizedWorkspaceRoot)) {
            throw new Error(`Path '${filePath}' resolves outside the workspace boundary.`);
        }

        return resolvedPath;
    }
}

module.exports = PathResolver;
