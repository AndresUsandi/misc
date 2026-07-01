const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function findModuleDependencies(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";

    try {
        let absPath;
        if (path.isAbsolute(filePath)) {
            absPath = filePath;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, filePath);
            } else {
                return `Error: Could not resolve relative path '${filePath}' because no workspace folders are open.`;
            }
        }

        if (!fs.existsSync(absPath)) {
            return `Error: File not found at '${absPath}'`;
        }

        const content = fs.readFileSync(absPath, 'utf8');
        
        // Match require('...') or require("...")
        const requireRegex = /require\(['"]([^'"]+)['"]\)/g;
        // Match import ... from '...' or import '...'
        const importRegex = /import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]/g;
        // Match export ... from '...'
        const exportRegex = /export\s+.*?\s+from\s+['"]([^'"]+)['"]/g;

        const dependencies = new Set();
        let match;

        while ((match = requireRegex.exec(content)) !== null) {
            dependencies.add(match[1]);
        }
        while ((match = importRegex.exec(content)) !== null) {
            dependencies.add(match[1]);
        }
        while ((match = exportRegex.exec(content)) !== null) {
            dependencies.add(match[1]);
        }

        let output = `=== Module Dependencies for ${vscode.workspace.asRelativePath(absPath)} ===\n\n`;
        if (dependencies.size > 0) {
            const sorted = Array.from(dependencies).sort();
            for (const dep of sorted) {
                output += `  - ${dep}\n`;
            }
        } else {
            output += `No dependencies found.\n`;
        }

        return output;
    } catch (e) {
        return `Error finding module dependencies: ${e.message}`;
    }
}

module.exports = findModuleDependencies;
