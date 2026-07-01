const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function findCycles(directory) {
    if (!directory) return "Error: Missing directory parameter.";

    try {
        let absPath;
        if (path.isAbsolute(directory)) {
            absPath = directory;
        } else {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (workspaceFolders && workspaceFolders.length > 0) {
                absPath = path.resolve(workspaceFolders[0].uri.fsPath, directory);
            } else {
                return `Error: Could not resolve relative path '${directory}' because no workspace folders are open.`;
            }
        }

        if (!fs.existsSync(absPath)) return `Error: Directory not found at '${absPath}'`;

        // 1. Gather all JS/TS files
        const files = await vscode.workspace.findFiles(
            new vscode.RelativePattern(absPath, '**/*.{js,ts,jsx,tsx}'),
            '**/node_modules/**'
        );

        const graph = new Map();

        // 2. Build graph
        for (const uri of files) {
            const content = fs.readFileSync(uri.fsPath, 'utf8');
            const deps = new Set();
            
            const requireRegex = /require\(['"]([^'"]+)['"]\)/g;
            const importRegex = /import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]/g;
            const exportRegex = /export\s+.*?\s+from\s+['"]([^'"]+)['"]/g;

            let match;
            while ((match = requireRegex.exec(content)) !== null) deps.add(match[1]);
            while ((match = importRegex.exec(content)) !== null) deps.add(match[1]);
            while ((match = exportRegex.exec(content)) !== null) deps.add(match[1]);

            // Resolve relative paths
            const resolvedDeps = [];
            for (const dep of deps) {
                if (dep.startsWith('.')) {
                    // Extremely simplified resolution for testing
                    let resolved = path.resolve(path.dirname(uri.fsPath), dep);
                    if (!resolved.match(/\.[tj]sx?$/)) resolved += '.js';
                    resolvedDeps.push(resolved);
                }
            }
            graph.set(uri.fsPath, resolvedDeps);
        }

        // 3. Find cycles using DFS
        const cycles = [];
        const visited = new Set();
        const recursionStack = new Set();
        const parentMap = new Map();

        function dfs(node) {
            visited.add(node);
            recursionStack.add(node);

            const neighbors = graph.get(node) || [];
            for (const neighbor of neighbors) {
                if (!visited.has(neighbor)) {
                    parentMap.set(neighbor, node);
                    dfs(neighbor);
                } else if (recursionStack.has(neighbor)) {
                    // Cycle detected!
                    const cycle = [neighbor];
                    let curr = node;
                    while (curr !== neighbor && curr) {
                        cycle.push(curr);
                        curr = parentMap.get(curr);
                    }
                    cycle.push(neighbor);
                    cycles.push(cycle.reverse());
                }
            }
            recursionStack.delete(node);
        }

        for (const node of graph.keys()) {
            if (!visited.has(node)) {
                dfs(node);
            }
        }

        if (cycles.length === 0) {
            return `=== Circular Dependencies in ${vscode.workspace.asRelativePath(absPath)} ===\n\nNo circular dependencies found.`;
        }

        let output = `=== Circular Dependencies Found (${cycles.length}) ===\n\n`;
        cycles.forEach((cycle, index) => {
            output += `Cycle ${index + 1}:\n`;
            for (const file of cycle) {
                output += `  -> ${vscode.workspace.asRelativePath(file)}\n`;
            }
            output += `\n`;
        });

        return output;
    } catch (e) {
        return `Error finding cycles: ${e.message}`;
    }
}

module.exports = findCycles;
