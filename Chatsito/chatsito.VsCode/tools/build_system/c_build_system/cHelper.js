const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const { exec } = require('child_process');

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

function getCBuildSystem(absPath) {
    let dirPath = absPath;
    try {
        if (fs.statSync(absPath).isFile()) {
            dirPath = path.dirname(absPath);
        }
    } catch(e) {}

    const hasCMake = fs.existsSync(path.join(dirPath, 'CMakeLists.txt'));
    const hasMakefile = fs.existsSync(path.join(dirPath, 'Makefile')) || fs.existsSync(path.join(dirPath, 'makefile'));

    if (hasCMake) {
        return { type: 'cmake', dirPath };
    }
    if (hasMakefile) {
        const makeExec = process.platform === 'win32' ? 'mingw32-make' : 'make';
        return { type: 'make', executable: makeExec, dirPath };
    }

    return { type: 'gcc', dirPath };
}

async function runCCommand(projectPath, cmakeCmd, makeCmd, gccCmd) {
    const absPath = resolvePath(projectPath);
    const system = getCBuildSystem(absPath);
    
    let command;
    if (system.type === 'cmake') {
        command = cmakeCmd;
    } else if (system.type === 'make') {
        command = makeCmd.replace(/\bmake\b/g, system.executable);
    } else {
        command = gccCmd;
    }

    return new Promise(resolve => {
        exec(command, { cwd: system.dirPath, maxBuffer: 1024 * 1024 * 10 }, (err, stdout, stderr) => {
            let output = `=== C/C++ Command: ${command} ===\n\n`;
            if (stdout) output += stdout;
            if (stderr) output += `\nErrors:\n${stderr}`;
            if (err && !stdout && !stderr) output += `\nFailed to execute: ${err.message}`;
            resolve(output.trim());
        });
    });
}

module.exports = {
    resolvePath,
    getCBuildSystem,
    runCCommand
};
