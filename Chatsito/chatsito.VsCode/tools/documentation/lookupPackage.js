const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

async function lookupPackage(packageName) {
    if (!packageName) return "Error: Missing packageName parameter.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const pkg = String(packageName);

        // Check Node.js package.json
        const packageJsonPath = path.join(rootPath, 'package.json');
        if (fs.existsSync(packageJsonPath)) {
            const content = fs.readFileSync(packageJsonPath, 'utf8');
            const parsed = JSON.parse(content);
            const deps = { ...parsed.dependencies, ...parsed.devDependencies };
            if (deps[pkg]) {
                return `Found package "${pkg}" in package.json. Version: ${deps[pkg]}`;
            }
        }

        // Check C# .csproj
        const pattern = new vscode.RelativePattern(rootPath, '**/*.csproj');
        const csprojFiles = await vscode.workspace.findFiles(pattern, '**/node_modules/**');
        
        for (const file of csprojFiles) {
            const content = fs.readFileSync(file.fsPath, 'utf8');
            // Regex to find <PackageReference Include="packageName" Version="1.2.3" />
            const regex = new RegExp(`<PackageReference\\s+Include=["']${pkg}["']\\s+Version=["']([^"']+)["']`, 'i');
            const match = content.match(regex);
            if (match && match[1]) {
                return `Found package "${pkg}" in ${vscode.workspace.asRelativePath(file.fsPath)}. Version: ${match[1]}`;
            }
        }

        return `Package "${pkg}" not found in package.json or .csproj files.`;

    } catch (e) {
        return `Error looking up package: ${e.message}`;
    }
}

module.exports = lookupPackage;
