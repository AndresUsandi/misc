const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function createTask(description) {
    if (!description) return "Error: Missing description parameter.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const chatsitoDir = path.join(rootPath, '.chatsito');
        
        if (!fs.existsSync(chatsitoDir)) {
            fs.mkdirSync(chatsitoDir, { recursive: true });
        }

        const tasksPath = path.join(chatsitoDir, 'tasks.json');
        
        let tasksObj = { tasks: [] };
        if (fs.existsSync(tasksPath)) {
            tasksObj = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
        }

        const newTaskId = tasksObj.tasks.length > 0 ? tasksObj.tasks[tasksObj.tasks.length - 1].id + 1 : 1;

        tasksObj.tasks.push({
            id: newTaskId,
            description: String(description).trim(),
            completed: false,
            createdAt: new Date().toISOString()
        });

        fs.writeFileSync(tasksPath, JSON.stringify(tasksObj, null, 2), 'utf8');

        return `Task created successfully with ID ${newTaskId}.`;

    } catch (e) {
        return `Error creating task: ${e.message}`;
    }
}

module.exports = createTask;
