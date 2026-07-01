const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const findModuleDependencies = require('./findModuleDependencies.js');

async function analyzeLayering(directory, rulesJsonStr) {
    if (!directory) return "Error: Missing directory parameter.";
    if (!rulesJsonStr) return "Error: Missing rulesJsonStr parameter. Provide JSON mapping layers to allowed dependencies.";

    try {
        let absPath;
        if (path.isAbsolute(directory)) {
            absPath = directory;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, directory);
            } else {
                return `Error: Could not resolve relative path '${directory}'.`;
            }
        }

        if (!fs.existsSync(absPath)) return `Error: Directory not found at '${absPath}'`;

        let rules;
        try {
            rules = JSON.parse(rulesJsonStr);
        } catch(e) {
            return `Error: Invalid rules JSON string. ${e.message}`;
        }

        const files = await vscode.workspace.findFiles(
            new vscode.RelativePattern(absPath, '**/*.{js,ts,jsx,tsx}'),
            '**/node_modules/**'
        );

        // Map files to layers based on path segments
        const getLayer = (fsPath) => {
            const rel = vscode.workspace.asRelativePath(fsPath);
            const segments = rel.replace(/\\/g, '/').split('/');
            for (const layer of Object.keys(rules)) {
                if (segments.includes(layer)) return layer;
            }
            return null;
        };

        const violations = [];

        for (const uri of files) {
            const layer = getLayer(uri.fsPath);
            if (!layer) continue; // Not part of any defined layer

            const content = fs.readFileSync(uri.fsPath, 'utf8');
            const deps = new Set();
            const requireRegex = /require\(['"]([^'"]+)['"]\)/g;
            const importRegex = /import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]/g;

            let match;
            while ((match = requireRegex.exec(content)) !== null) deps.add(match[1]);
            while ((match = importRegex.exec(content)) !== null) deps.add(match[1]);

            for (const dep of deps) {
                if (dep.startsWith('.')) {
                    // Resolve relative import to layer
                    let resolved = path.resolve(path.dirname(uri.fsPath), dep);
                    if (!resolved.match(/\.[tj]sx?$/)) resolved += '.js';
                    
                    const targetLayer = getLayer(resolved);
                    if (targetLayer && targetLayer !== layer) {
                        const allowed = rules[layer] || [];
                        if (!allowed.includes(targetLayer)) {
                            violations.push({
                                file: vscode.workspace.asRelativePath(uri.fsPath),
                                importPath: dep,
                                fromLayer: layer,
                                toLayer: targetLayer
                            });
                        }
                    }
                }
            }
        }

        if (violations.length === 0) {
            return `=== Layering Analysis ===\n\nNo layering violations found.`;
        }

        let output = `=== Layering Violations Found (${violations.length}) ===\n\n`;
        for (const v of violations) {
            output += `  - [VIOLATION] ${v.file} (${v.fromLayer}) illegally imports ${v.importPath} (${v.toLayer})\n`;
        }

        return output;

    } catch (e) {
        return `Error analyzing layering: ${e.message}`;
    }
}

module.exports = analyzeLayering;
