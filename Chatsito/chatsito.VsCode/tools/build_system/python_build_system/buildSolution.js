const buildProject = require('./buildProject');

async function buildSolution(solutionPath) {
    return await buildProject(solutionPath);
}

module.exports = buildSolution;
