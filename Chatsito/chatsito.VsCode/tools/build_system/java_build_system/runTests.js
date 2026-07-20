const { runJavaCommand } = require('./javaHelper');

async function runTests(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    return await runJavaCommand(projectPath, 'test', 'test');
}

module.exports = runTests;
