const { runJavaCommand } = require('./javaHelper');

async function runTest(projectPath, testName) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    if (!testName) return "Error: Missing testName parameter.";

    return await runJavaCommand(projectPath, `test -Dtest="${testName}"`, `test --tests "${testName}"`);
}

module.exports = runTest;
