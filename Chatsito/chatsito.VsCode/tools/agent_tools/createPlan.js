const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function createPlan(stepsInput) {
    if (!stepsInput) return "Error: Missing stepsInput parameter.";

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

        const planPath = path.join(chatsitoDir, 'plan.json');
        
        let steps = [];
        if (Array.isArray(stepsInput)) {
            steps = stepsInput.map(s => String(s));
        } else if (typeof stepsInput === 'string') {
            steps = stepsInput.split('\n').map(s => s.trim()).filter(s => s.length > 0);
        } else {
            return "Error: stepsInput must be an array or string.";
        }

        const planObj = {
            created: new Date().toISOString(),
            steps: steps.map(s => ({ description: s, completed: false }))
        };

        fs.writeFileSync(planPath, JSON.stringify(planObj, null, 2), 'utf8');

        return `Plan created successfully with ${steps.length} steps.\nSaved to ${vscode.workspace.asRelativePath(planPath)}`;

    } catch (e) {
        return `Error creating plan: ${e.message}`;
    }
}

module.exports = createPlan;
