const { forwardToolRequest } = require('./forwarder');

async function runTests(projectPath) {
    return await forwardToolRequest('runTests', projectPath);
}

module.exports = runTests;
