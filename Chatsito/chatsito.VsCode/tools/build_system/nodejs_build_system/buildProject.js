const { runNodeCommand, resolvePath } = require('./nodeHelper');
const fs = require('fs');
const path = require('path');

async function buildProject(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    const absPath = resolvePath(projectPath);
    let command = "";

    try {
        const files = fs.readdirSync(absPath).map(f => f.toLowerCase());
        
        // 1. Dependency restoration check
        let restoreCmd = "";
        if (files.includes('package.json')) {
            const pkg = JSON.parse(fs.readFileSync(path.join(absPath, 'package.json'), 'utf8'));
            const hasDeps = (pkg.dependencies && Object.keys(pkg.dependencies).length > 0) ||
                            (pkg.devDependencies && Object.keys(pkg.devDependencies).length > 0);
            
            const hasNodeModules = files.includes('node_modules');
            if (hasDeps && !hasNodeModules) {
                if (files.includes('pnpm-lock.yaml')) {
                    restoreCmd = "pnpm install && ";
                } else if (files.includes('yarn.lock')) {
                    restoreCmd = "yarn install && ";
                } else {
                    restoreCmd = "npm install && ";
                }
            }
        }

        // 2. Build or Lint command selection
        let buildCmd = "";
        if (files.includes('package.json')) {
            const pkg = JSON.parse(fs.readFileSync(path.join(absPath, 'package.json'), 'utf8'));
            if (pkg.scripts && pkg.scripts.build) {
                buildCmd = "npm run build";
            }
        }
        
        if (!buildCmd) {
            if (files.includes('tsconfig.json')) {
                buildCmd = "npx tsc --noEmit";
            } else if (files.includes('.eslintrc') || files.includes('.eslintrc.json') || files.includes('eslint.config.js') || files.includes('eslint.config.mjs')) {
                buildCmd = "npx eslint .";
            } else {
                const jsFiles = fs.readdirSync(absPath).filter(f => f.endsWith('.js') && f !== 'node_modules');
                if (jsFiles.length > 0) {
                    buildCmd = jsFiles.map(f => `node --check "${f}"`).join(' && ');
                } else {
                    buildCmd = "echo 'No build script, tsconfig, eslint configuration, or javascript files found to check.'";
                }
            }
        }

        command = restoreCmd + buildCmd;

    } catch (e) {
        command = "npm run build";
    }

    return await runNodeCommand(projectPath, command, "Build Results", "Build succeeded.");
}

module.exports = buildProject;
