const { forwardToolRequest } = require('./forwarder');

async function buildProject(projectPath) {
    return await forwardToolRequest('buildProject', projectPath);
}

module.exports = buildProject;
