const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

async function listDirectory(dirPath) {
    try {
        let resolvedPath;
        try {
            if (!dirPath || dirPath.trim() === '') {
                const workspaceFolders = vscode.workspace.workspaceFolders;
                if (!workspaceFolders || workspaceFolders.length === 0) {
                    return "Error: No directory path provided and no workspace folder is open.";
                }
                resolvedPath = workspaceFolders[0].uri.fsPath;
            } else {
                const PathResolver = require('../../PathResolver');
                resolvedPath = PathResolver.resolveAndValidateWorkspacePath(dirPath);
            }
        } catch (err) {
            return `Error: ${err.message}`;
        }

        if (!fs.existsSync(resolvedPath)) {
            return `Error: Directory does not exist: ${resolvedPath}`;
        }

        const stat = fs.statSync(resolvedPath);
        if (!stat.isDirectory()) {
            return `Error: Path is not a directory: ${resolvedPath}`;
        }

        const files = fs.readdirSync(resolvedPath, { withFileTypes: true });
        
        let output = `=== Directory Contents: ${vscode.workspace.asRelativePath(resolvedPath)} ===\n\n`;
        
        const directories = [];
        const fileList = [];

        for (const file of files) {
            if (file.isDirectory()) {
                directories.push(file.name);
            } else if (file.isFile()) {
                fileList.push(file.name);
            }
        }

        directories.sort();
        fileList.sort();

        if (directories.length === 0 && fileList.length === 0) {
            output += "(directory is empty)";
            return output;
        }

        if (directories.length > 0) {
            output += `[Directories]\n`;
            for (const d of directories) {
                output += `  ${d}/\n`;
            }
            output += `\n`;
        }

        if (fileList.length > 0) {
            output += `[Files]\n`;
            for (const f of fileList) {
                output += `  ${f}\n`;
            }
        }

        return output.trim();
    } catch (error) {
        return `Error listing directory: ${error.message}`;
    }
}

module.exports = listDirectory;
