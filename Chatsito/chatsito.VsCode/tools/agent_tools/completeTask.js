const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function completeTask(taskIdStr) {
    if (!taskIdStr) return "Error: Missing taskId parameter.";

    const taskId = parseInt(taskIdStr, 10);
    if (isNaN(taskId)) return "Error: taskId must be a valid number.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const tasksPath = path.join(rootPath, '.chatsito', 'tasks.json');
        
        if (!fs.existsSync(tasksPath)) {
            return "Error: No tasks found. Use createTask first.";
        }

        const tasksObj = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
        const task = tasksObj.tasks.find(t => t.id === taskId);

        if (!task) {
            return `Error: Task with ID ${taskId} not found.`;
        }

        task.completed = true;
        fs.writeFileSync(tasksPath, JSON.stringify(tasksObj, null, 2), 'utf8');

        return `Task ${taskId} marked as complete: "${task.description}"`;

    } catch (e) {
        return `Error completing task: ${e.message}`;
    }
}

module.exports = completeTask;
