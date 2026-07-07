import vscode from '../../vscode.js';
import path from 'path';
import fs from 'fs';
import PathResolver from '../../PathResolver.js';

async function readFile(filePath) {
    if (!filePath) {
        return "Error: No file path provided.";
    }

    try {
        let absolutePath;
        try {
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

export default readFile;
