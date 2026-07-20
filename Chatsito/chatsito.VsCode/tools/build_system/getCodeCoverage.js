const { forwardToolRequest } = require('./forwarder');

async function getCodeCoverage(projectPath) {
    return await forwardToolRequest('getCodeCoverage', projectPath);
}

module.exports = getCodeCoverage;
