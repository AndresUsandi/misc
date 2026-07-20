const { runNodeCommand, resolvePath } = require('./nodeHelper');
const fs = require('fs');
const path = require('path');

async function runTests(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    const absPath = resolvePath(projectPath);
    let command = "npm test || node --test || npx jest || npx mocha";

    try {
        const files = fs.readdirSync(absPath).map(f => f.toLowerCase());
        if (files.includes('package.json')) {
            const pkg = JSON.parse(fs.readFileSync(path.join(absPath, 'package.json'), 'utf8'));
            if (pkg.scripts && pkg.scripts.test && pkg.scripts.test !== 'echo "Error: no test specified" && exit 1') {
                command = "npm test";
            }
        }
    } catch (e) {}

    return await runNodeCommand(projectPath, command, "Test Results");
}

module.exports = runTests;
