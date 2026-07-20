const { runPythonCommand, resolvePath } = require('./pythonHelper');
const fs = require('fs');
const path = require('path');

async function buildProject(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    
    const absPath = resolvePath(projectPath);
    let command = "python -m py_compile *.py || python -m py_compile **/*.py";
    
    try {
        const files = fs.readdirSync(absPath).map(f => f.toLowerCase());
        if (files.includes('requirements.txt')) {
            command = "pip install -r requirements.txt && " + command;
        } else if (files.includes('pyproject.toml')) {
            command = "poetry install && " + command;
        } else if (files.includes('setup.py')) {
            command = "python setup.py build && " + command;
        }
    } catch(e) {}

    return await runPythonCommand(projectPath, command);
}

module.exports = buildProject;
