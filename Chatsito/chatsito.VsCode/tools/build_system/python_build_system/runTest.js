const { runPythonCommand } = require('./pythonHelper');

async function runTest(projectPath, testName) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    if (!testName) return "Error: Missing testName parameter.";

    return await runPythonCommand(
        projectPath, 
        `pytest -k "${testName}" || python -m unittest -k "${testName}"`
    );
}

module.exports = runTest;
