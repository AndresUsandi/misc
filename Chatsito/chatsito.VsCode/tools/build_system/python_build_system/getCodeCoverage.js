const { runPythonCommand } = require('./pythonHelper');

async function getCodeCoverage(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";

    return await runPythonCommand(
        projectPath, 
        "pytest --cov=. || coverage run -m pytest || coverage run -m unittest discover && coverage report"
    );
}

module.exports = getCodeCoverage;
