const compileFileNode = require('../nodejs_build_system/compileFile');

async function compileFile(filePath) {
    return await compileFileNode(filePath);
}

module.exports = compileFile;
