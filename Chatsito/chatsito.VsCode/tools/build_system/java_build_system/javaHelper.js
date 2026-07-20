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

function getJavaBuildSystem(absPath) {
    const isWindows = process.platform === 'win32';
    
    // Check if path is a file, if so get its directory
    let dirPath = absPath;
    try {
        if (fs.statSync(absPath).isFile()) {
            dirPath = path.dirname(absPath);
        }
    } catch(e) {}

    const hasPom = fs.existsSync(path.join(dirPath, 'pom.xml'));
    const hasGradle = fs.existsSync(path.join(dirPath, 'build.gradle')) || fs.existsSync(path.join(dirPath, 'build.gradle.kts'));
    
    if (hasGradle) {
        let gradlew = isWindows ? 'gradlew.bat' : './gradlew';
        if (fs.existsSync(path.join(dirPath, gradlew))) {
            return { type: 'gradle', executable: gradlew, dirPath };
        }
        return { type: 'gradle', executable: 'gradle', dirPath };
    }
    
    // Default to Maven
    return { type: 'maven', executable: 'mvn', dirPath };
}

async function runJavaCommand(projectPath, mavenArgs, gradleArgs) {
    const absPath = resolvePath(projectPath);
    const system = getJavaBuildSystem(absPath);
    
    const commandArgs = system.type === 'maven' ? mavenArgs : gradleArgs;
    const command = `${system.executable} ${commandArgs}`;

    return new Promise(resolve => {
        exec(command, { cwd: system.dirPath, maxBuffer: 1024 * 1024 * 10 }, (err, stdout, stderr) => {
            let output = `=== Java Command: ${command} ===\n\n`;
            if (stdout) output += stdout;
            if (stderr) output += `\nErrors:\n${stderr}`;
            if (err && !stdout && !stderr) output += `\nFailed to execute: ${err.message}`;
            resolve(output.trim());
        });
    });
}

module.exports = {
    resolvePath,
    getJavaBuildSystem,
    runJavaCommand
};
