const runFileNode = require('../nodejs_build_system/runFile');

async function runFile(filePath, runArgs) {
    return await runFileNode(filePath, runArgs);
}

module.exports = runFile;
