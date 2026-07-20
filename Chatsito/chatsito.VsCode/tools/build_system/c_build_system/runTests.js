const { runCCommand } = require('./cHelper');

async function runTests(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    return await runCCommand(
        projectPath, 
        'ctest', 
        './test_runner || make test', 
        './test_runner || ./main'
    );
}

module.exports = runTests;
