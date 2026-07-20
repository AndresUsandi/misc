const { exec } = require('child_process');
const { resolvePath } = require('./javaHelper');

async function compileFile(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    const command = `javac "${absPath}"`;
    
    return new Promise(resolve => {
        exec(command, (err, stdout, stderr) => {
            let output = `=== Java Compilation Results ===\n\n`;
            if (stdout) output += `STDOUT:\n${stdout}\n`;
            if (stderr) output += `STDERR:\n${stderr}\n`;
            if (err) {
                output += `\nError: Compilation failed with code ${err.code}\n${err.message}`;
            } else {
                output += `\nCompilation succeeded.`;
            }
            resolve(output.trim());
        });
    });
}

module.exports = compileFile;
