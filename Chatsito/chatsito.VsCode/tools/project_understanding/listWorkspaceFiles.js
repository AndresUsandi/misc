const vscode = require('vscode');

async function listWorkspaceFiles(filterGlob) {
    try {
        const pattern = filterGlob && filterGlob.trim() !== '' ? filterGlob : '**/*';
        const uris = await vscode.workspace.findFiles(pattern, '{**/node_modules/**,**/.git/**,**/bin/**,**/obj/**,**/.vs/**,**/.vscode-test/**}');
        if (uris.length === 0) {
            return "No files found in workspace matching pattern: " + pattern;
        }

        let filePaths = uris.map(uri => vscode.workspace.asRelativePath(uri));
        filePaths.sort();

        // If there are too many files, truncate the list
        const maxFiles = 200;
        let output = `=== Workspace Files (${filePaths.length} found) ===\n\n`;
        if (filePaths.length > maxFiles) {
            output += filePaths.slice(0, maxFiles).join('\n') + `\n\n... and ${filePaths.length - maxFiles} more files (truncated).`;
        } else {
            output += filePaths.join('\n');
        }
        return output;
    } catch (error) {
        return `Error listing workspace files: ${error.message}`;
    }
}

module.exports = listWorkspaceFiles;
