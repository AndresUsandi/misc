const { runPythonCommand, resolvePath } = require('./pythonHelper');

async function compileFile(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    return await runPythonCommand(filePath, `python -m py_compile "${absPath}"`, "Python Compile Results", "File compiled successfully.");
}

module.exports = compileFile;
