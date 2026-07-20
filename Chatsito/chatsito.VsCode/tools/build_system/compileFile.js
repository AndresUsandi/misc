const { forwardToolRequest } = require('./forwarder');

async function compileFile(filePath) {
    return await forwardToolRequest('compileFile', filePath);
}

module.exports = compileFile;
