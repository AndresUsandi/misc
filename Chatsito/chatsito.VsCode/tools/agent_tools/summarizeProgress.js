const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function summarizeProgress() {
    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const planPath = path.join(rootPath, '.chatsito', 'plan.json');
        const tasksPath = path.join(rootPath, '.chatsito', 'tasks.json');
        
        let output = `=== Progress Summary ===\n\n`;

        // Summarize Plan
        if (fs.existsSync(planPath)) {
            const planObj = JSON.parse(fs.readFileSync(planPath, 'utf8'));
            const completed = planObj.steps.filter(s => s.completed).length;
            const total = planObj.steps.length;
            output += `## Plan Progress (${completed}/${total} completed)\n`;
            
            planObj.steps.forEach((s, idx) => {
                const mark = s.completed ? '[x]' : '[ ]';
                output += `- ${mark} Step ${idx}: ${s.description}\n`;
            });
            output += '\n';
        } else {
            output += `## Plan Progress\nNo active plan.\n\n`;
        }

        // Summarize Tasks
        if (fs.existsSync(tasksPath)) {
            const tasksObj = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
            const completed = tasksObj.tasks.filter(t => t.completed).length;
            const total = tasksObj.tasks.length;
            output += `## Tasks Progress (${completed}/${total} completed)\n`;
            
            tasksObj.tasks.forEach(t => {
                const mark = t.completed ? '[x]' : '[ ]';
                output += `- ${mark} Task ${t.id}: ${t.description}\n`;
            });
        } else {
            output += `## Tasks Progress\nNo active tasks.\n`;
        }

        return output;

    } catch (e) {
        return `Error summarizing progress: ${e.message}`;
    }
}

module.exports = summarizeProgress;
