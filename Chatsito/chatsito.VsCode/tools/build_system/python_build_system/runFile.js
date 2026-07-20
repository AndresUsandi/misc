const { runPythonCommand, resolvePath } = require('./pythonHelper');

async function runFile(filePath, runArgs) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    const argsStr = runArgs ? ` ${runArgs}` : '';
    return await runPythonCommand(filePath, `python "${absPath}"${argsStr}`, "Python Execution Results", "Execution completed.");
}

module.exports = runFile;
