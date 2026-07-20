const { runNodeCommand, resolvePath } = require('./nodeHelper');
const path = require('path');

async function runFile(filePath, runArgs) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    const ext = path.extname(absPath).toLowerCase();
    const argsStr = runArgs ? ` ${runArgs}` : '';
    
    let command;
    if (ext === '.ts' || ext === '.tsx') {
        command = `npx ts-node "${absPath}"${argsStr}`;
    } else {
        command = `node "${absPath}"${argsStr}`;
    }
    
    return await runNodeCommand(filePath, command, "Node/TypeScript Run Results", "Execution completed.");
}

module.exports = runFile;
