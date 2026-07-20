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
            const projectFile = files.find(f => f.endsWith('.csproj') || f.endsWith('.sln'));
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

async function compileFile(filePath) {
    if (!filePath) return "Error: Missing filePath parameter.";
    const absPath = resolvePath(filePath);
    
    const projectPath = findDotnetProject(path.dirname(absPath));
    let command;
    if (projectPath) {
        command = `dotnet build "${projectPath}"`;
    } else {
        command = `csc "${absPath}"`;
    }
    
    return new Promise(resolve => {
        exec(command, (err, stdout, stderr) => {
            let output = `=== Dotnet Compilation Results ===\n\n`;
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
