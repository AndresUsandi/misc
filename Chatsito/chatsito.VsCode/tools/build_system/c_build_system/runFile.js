const { exec } = require('child_process');
const { resolvePath } = require('./cHelper');
const path = require('path');
const fs = require('fs');

async function runFile(filePath, runArgs) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    const ext = path.extname(absPath).toLowerCase();
    const dir = path.dirname(absPath);
    const compiler = (ext === '.c') ? 'gcc' : 'g++';
    
    const isWindows = process.platform === 'win32';
    const binaryName = `temp_run_${Date.now()}${isWindows ? '.exe' : ''}`;
    const binaryPath = path.join(dir, binaryName);
    
    const compileCmd = `${compiler} "${absPath}" -o "${binaryPath}"`;
    
    return new Promise(resolve => {
        exec(compileCmd, (cErr, cStdout, cStderr) => {
            if (cErr) {
                let output = `=== C/C++ Compilation Failed ===\n\n`;
                if (cStdout) output += `STDOUT:\n${cStdout}\n`;
                if (cStderr) output += `STDERR:\n${cStderr}\n`;
                output += `\nError: ${cErr.message}`;
                return resolve(output.trim());
            }
            
            const argsStr = runArgs ? ` ${runArgs}` : '';
            const runCmd = isWindows ? `"${binaryPath}"${argsStr}` : `./${binaryName}${argsStr}`;
            
            exec(runCmd, { cwd: dir }, (rErr, rStdout, rStderr) => {
                let output = `=== C/C++ Run Results ===\n\n`;
                if (rStdout) output += `STDOUT:\n${rStdout}\n`;
                if (rStderr) output += `STDERR:\n${rStderr}\n`;
                if (rErr) {
                    output += `\nError: Run failed with code ${rErr.code}\n${rErr.message}`;
                } else {
                    output += `\nExecution completed.`;
                }
                
                // Cleanup binary
                try {
                    if (fs.existsSync(binaryPath)) {
                        fs.unlinkSync(binaryPath);
                    }
                } catch(e) {}
                
                resolve(output.trim());
            });
        });
    });
}

module.exports = runFile;
