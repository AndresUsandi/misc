const { exec } = require('child_process');
const { resolvePath } = require('./cHelper');
const path = require('path');

async function compileFile(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    const ext = path.extname(absPath).toLowerCase();
    const compiler = (ext === '.c') ? 'gcc' : 'g++';
    const command = `${compiler} -fsyntax-only "${absPath}"`;
    
    return new Promise(resolve => {
        exec(command, (err, stdout, stderr) => {
            let output = `=== C/C++ Syntax Check Results ===\n\n`;
            if (stdout) output += `STDOUT:\n${stdout}\n`;
            if (stderr) output += `STDERR:\n${stderr}\n`;
            if (err) {
                output += `\nError: Syntax check failed with code ${err.code}\n${err.message}`;
            } else {
                output += `\nSyntax check completed successfully. No syntax errors detected.`;
            }
            resolve(output.trim());
        });
    });
}

module.exports = compileFile;
