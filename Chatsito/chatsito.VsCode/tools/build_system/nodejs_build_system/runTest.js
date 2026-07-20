const { runNodeCommand, resolvePath } = require('./nodeHelper');
const fs = require('fs');
const path = require('path');

async function runTest(projectPath, testName) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    if (!testName) return "Error: Missing testName parameter.";

    const absPath = resolvePath(projectPath);
    let command = `npm test -- -g "${testName}" || node --test --test-name-pattern="${testName}" || npx jest -t "${testName}" || npx mocha -g "${testName}"`;

    try {
        const files = fs.readdirSync(absPath).map(f => f.toLowerCase());
        if (files.includes('package.json')) {
            const pkg = JSON.parse(fs.readFileSync(path.join(absPath, 'package.json'), 'utf8'));
            if (pkg.scripts && pkg.scripts.test && pkg.scripts.test !== 'echo "Error: no test specified" && exit 1') {
                if (pkg.scripts.test.includes('jest')) {
                    command = `npm test -- -t "${testName}"`;
                } else {
                    command = `npm test -- -g "${testName}"`;
                }
            }
        }
    } catch (e) {}

    return await runNodeCommand(projectPath, command, "Specific Test Results", `Test '${testName}' passed successfully.`);
}

module.exports = runTest;
