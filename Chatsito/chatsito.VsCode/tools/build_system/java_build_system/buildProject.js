const { runJavaCommand } = require('./javaHelper');

async function buildProject(projectPath) {
    if (!projectPath) return "Error: Missing projectPath parameter.";
    return await runJavaCommand(projectPath, 'compile', 'compileJava');
}

module.exports = buildProject;
