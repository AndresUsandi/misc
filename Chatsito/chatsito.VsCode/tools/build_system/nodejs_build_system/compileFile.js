const { runNodeCommand, resolvePath } = require('./nodeHelper');
const path = require('path');

async function compileFile(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    const ext = path.extname(absPath).toLowerCase();
    
    let command;
    if (ext === '.ts' || ext === '.tsx') {
        command = `npx tsc --noEmit "${absPath}"`;
    } else {
        command = `node --check "${absPath}"`;
    }
    
    return await runNodeCommand(filePath, command, "Node/TypeScript Compile Results", "File compilation/syntax check succeeded.");
}

module.exports = compileFile;
