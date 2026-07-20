const vscode = require('vscode');
const path = require('path');
const fs = require('fs');

async function readFile(filePath) {
    if (!filePath) {
        return "Error: No file path provided.";
    }

    try {
        let absolutePath;
        try {
            const PathResolver = require('../../PathResolver');
            absolutePath = PathResolver.resolveAndValidateWorkspacePath(filePath);
        } catch (err) {
            return `Error: ${err.message}`;
        }

        if (!fs.existsSync(absolutePath)) {
            return `Error: File not found at '${absolutePath}'`;
        }

        const stats = fs.statSync(absolutePath);
        if (stats.isDirectory()) {
            return `Error: Path '${absolutePath}' is a directory, not a file.`;
        }

        const content = fs.readFileSync(absolutePath, 'utf8');
        return content;
    } catch (error) {
        return `Error reading file: ${error.message}`;
    }
}

module.exports = readFile;
