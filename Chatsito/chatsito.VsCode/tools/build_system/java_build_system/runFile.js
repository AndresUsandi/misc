const { exec } = require('child_process');
const { resolvePath } = require('./javaHelper');

async function runFile(filePath, runArgs) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    const argsStr = runArgs ? ` ${runArgs}` : '';
    const command = `java "${absPath}"${argsStr}`;
    
    return new Promise(resolve => {
        exec(command, (err, stdout, stderr) => {
            let output = `=== Java Execution Results ===\n\n`;
            if (stdout) output += `STDOUT:\n${stdout}\n`;
            if (stderr) output += `STDERR:\n${stderr}\n`;
            if (err) {
                output += `\nError: Execution failed with code ${err.code}\n${err.message}`;
            } else {
                output += `\nExecution completed.`;
            }
            resolve(output.trim());
        });
    });
}

module.exports = runFile;
