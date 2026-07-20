const { runPythonCommand } = require('./pythonHelper');

async function runTests(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    return await runPythonCommand(projectPath, "pytest || python -m unittest discover");
}

module.exports = runTests;
