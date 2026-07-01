const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function getProjectDependencies(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    try {
        let absPath;
        if (path.isAbsolute(projectPath)) {
            absPath = projectPath;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, projectPath);
            } else {
                return `Error: Could not resolve relative path '${projectPath}' because no workspace folders are open.`;
            }
        }

        const stats = fs.statSync(absPath);
        const dirPath = stats.isDirectory() ? absPath : path.dirname(absPath);
        const packageJsonPath = path.join(dirPath, 'package.json');

        if (!fs.existsSync(packageJsonPath)) {
            return `No package.json found in ${dirPath}`;
        }

        const packageData = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        let output = `=== Dependencies for ${packageData.name || 'Project'} ===\n\n`;

        if (packageData.dependencies) {
            output += `Dependencies:\n`;
            for (const [dep, ver] of Object.entries(packageData.dependencies)) {
                output += `  - ${dep}: ${ver}\n`;
            }
        } else {
            output += `No dependencies found.\n`;
        }

        if (packageData.devDependencies) {
            output += `\nDev Dependencies:\n`;
            for (const [dep, ver] of Object.entries(packageData.devDependencies)) {
                output += `  - ${dep}: ${ver}\n`;
            }
        }

        return output;
    } catch (e) {
        return `Error getting project dependencies: ${e.message}`;
    }
}

module.exports = getProjectDependencies;
