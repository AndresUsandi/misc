const { forwardToolRequest } = require('./forwarder');

async function listTests(projectPath) {
    return await forwardToolRequest('listTests', projectPath);
}

module.exports = listTests;
