const { runNodeCommand, resolvePath } = require('./nodeHelper');
const fs = require('fs');
const path = require('path');

async function getCodeCoverage(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    const absPath = resolvePath(projectPath);
    let command = "node --experimental-test-coverage --test || npx nyc npm test || npx nyc mocha";

    try {
        const files = fs.readdirSync(absPath).map(f => f.toLowerCase());
        if (files.includes('package.json')) {
            const pkg = JSON.parse(fs.readFileSync(path.join(absPath, 'package.json'), 'utf8'));
            if (pkg.scripts) {
                if (pkg.scripts.coverage) {
                    command = "npm run coverage";
                } else if (pkg.scripts.test) {
                    command = "npm test -- --coverage";
                }
            } else {
                command = "npm test -- --coverage";
            }
        }
    } catch (e) {}

    return await runNodeCommand(projectPath, command, "Code Coverage Results", "Coverage gathered successfully.");
}

module.exports = getCodeCoverage;
