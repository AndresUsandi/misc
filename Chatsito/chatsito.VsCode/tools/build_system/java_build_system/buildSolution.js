const { runJavaCommand } = require('./javaHelper');

async function buildSolution(solutionPath) {
    return await runJavaCommand(solutionPath, 'package -DskipTests', 'build -x test');
}

module.exports = buildSolution;
