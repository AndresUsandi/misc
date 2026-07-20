const { runCCommand } = require('./cHelper');

async function runTest(projectPath, testName) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    if (!testName) return "Error: Missing testName parameter.";

    return await runCCommand(
        projectPath, 
        `ctest -R "${testName}"`, 
        `./test_runner --gtest_filter="${testName}" || ./test_runner "${testName}" || make test`, 
        `./test_runner --gtest_filter="${testName}" || ./test_runner "${testName}" || ./main`
    );
}

module.exports = runTest;
