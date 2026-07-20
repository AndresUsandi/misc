const { forwardToolRequest } = require('./forwarder');

async function runFile(filePath, runArgs) {
    return await forwardToolRequest('runFile', filePath, runArgs);
}

module.exports = runFile;
