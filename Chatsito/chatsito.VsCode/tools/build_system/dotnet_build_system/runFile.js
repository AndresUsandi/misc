const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');

function resolvePath(targetPath) {
    if (!targetPath) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (workspaceFolders && workspaceFolders.length > 0) {
            return workspaceFolders[0].uri.fsPath;
        }
        return process.cwd();
    }
    if (path.isAbsolute(targetPath)) {
        return targetPath;
    }
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (workspaceFolders && workspaceFolders.length > 0) {
        return path.resolve(workspaceFolders[0].uri.fsPath, targetPath);
    }
    return path.resolve(targetPath);
}

function findDotnetProject(dir) {
    let currentDir = dir;
    const root = vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0 
        ? vscode.workspace.workspaceFolders[0].uri.fsPath 
        : null;

    while (currentDir) {
        try {
            const files = fs.readdirSync(currentDir);
            const projectFile = files.find(f => f.endsWith('.csproj'));
            if (projectFile) {
                return path.join(currentDir, projectFile);
            }
        } catch(e) {}
        
        if (currentDir === root || currentDir === path.dirname(currentDir)) {
            break;
        }
        currentDir = path.dirname(currentDir);
    }
    return null;
}

async function runFile(filePath, runArgs) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    
    const projectPath = findDotnetProject(path.dirname(absPath));
    if (projectPath) {
        const argsStr = runArgs ? ` -- ${runArgs}` : '';
        const command = `dotnet run --project "${projectPath}"${argsStr}`;
        return new Promise(resolve => {
            exec(command, (err, stdout, stderr) => {
                let output = `=== Dotnet Execution Results ===\n\n`;
                if (stdout) output += `STDOUT:\n${stdout}\n`;
                if (stderr) output += `STDERR:\n${stderr}\n`;
                if (err) {
                    output += `\nError: Run failed with code ${err.code}\n${err.message}`;
                } else {
                    output += `\nExecution completed.`;
                }
                resolve(output.trim());
            });
        });
    } else {
        const dir = path.dirname(absPath);
        const binaryName = `temp_run_${Date.now()}.exe`;
        const binaryPath = path.join(dir, binaryName);
        const compileCmd = `csc "${absPath}" /out:"${binaryPath}"`;
        
        return new Promise(resolve => {
            exec(compileCmd, (cErr, cStdout, cStderr) => {
                if (cErr) {
                    let output = `=== Dotnet Standalone Compilation Failed ===\n\n`;
                    if (cStdout) output += `STDOUT:\n${cStdout}\n`;
                    if (cStderr) output += `STDERR:\n${cStderr}\n`;
                    output += `\nError: ${cErr.message}`;
                    return resolve(output.trim());
                }
                
                const argsStr = runArgs ? ` ${runArgs}` : '';
                const runCmd = `"${binaryPath}"${argsStr}`;
                
                exec(runCmd, { cwd: dir }, (rErr, rStdout, rStderr) => {
                    let output = `=== Dotnet Standalone Execution Results ===\n\n`;
                    if (rStdout) output += `STDOUT:\n${rStdout}\n`;
                    if (rStderr) output += `STDERR:\n${rStderr}\n`;
                    if (rErr) {
                        output += `\nError: Run failed with code ${rErr.code}\n${rErr.message}`;
                    } else {
                        output += `\nExecution completed.`;
                    }
                    
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
}

module.exports = runFile;
