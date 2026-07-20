const { forwardToolRequest } = require('./forwarder');

async function buildSolution(solutionPath) {
    return await forwardToolRequest('buildSolution', solutionPath);
}

module.exports = buildSolution;
