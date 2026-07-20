const vscode = require('vscode');
const { exec } = require('child_process');

const ALLOWLIST = [
    'dotnet test',
    'dotnet build',
    'npm test',
    'npm run build',
    'pytest',
    'git status',
    'git log',
    'git diff',
    'git show',
    'node'
];

async function runCommand(command) {
    if (!command) return "Error: No command provided.";

    const cmdTrimmed = command.trim();
    const isAllowed = ALLOWLIST.some(prefix => cmdTrimmed === prefix || cmdTrimmed.startsWith(prefix + ' '));
    
    if (!isAllowed) {
        return `Error: Command "${command}" is not in the allowlist. Allowed prefixes: ${ALLOWLIST.join(', ')}`;
    }

    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
        return "Error: No workspace folder open.";
    }

    const rootPath = workspaceFolders[0].uri.fsPath;

    return new Promise((resolve) => {
        exec(command, { cwd: rootPath, timeout: 30000, maxBuffer: 500 * 1024 }, (error, stdout, stderr) => {
            let output = `=== Command Execution Output: "${command}" ===\n\n`;
            if (error) {
                if (error.killed) {
                    output += `Error: Command timed out after 30 seconds or exceeded output limits.\n`;
                } else {
                    output += `Error: ${error.message}\n`;
                }
            }
            output += `Stdout:\n${stdout || "(no stdout)"}\n\n`;
            output += `Stderr:\n${stderr || "(no stderr)"}\n`;
            resolve(output);
        });
    });
}

module.exports = runCommand;
