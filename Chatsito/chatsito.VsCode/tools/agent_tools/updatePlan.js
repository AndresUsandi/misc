const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function updatePlan(stepsInput) {
    if (!stepsInput) return "Error: Missing stepsInput parameter.";

    try {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders || workspaceFolders.length === 0) {
            return "Error: No workspace folder open.";
        }

        const rootPath = workspaceFolders[0].uri.fsPath;
        const planPath = path.join(rootPath, '.chatsito', 'plan.json');
        
        if (!fs.existsSync(planPath)) {
            return "Error: No active plan found. Use createPlan first.";
        }

        const planObj = JSON.parse(fs.readFileSync(planPath, 'utf8'));
        
        let newSteps = [];
        if (Array.isArray(stepsInput)) {
            newSteps = stepsInput.map(s => String(s));
        } else if (typeof stepsInput === 'string') {
            newSteps = stepsInput.split('\n').map(s => s.trim()).filter(s => s.length > 0);
        } else {
            return "Error: stepsInput must be an array or string.";
        }

        for (const s of newSteps) {
            planObj.steps.push({ description: s, completed: false });
        }

        fs.writeFileSync(planPath, JSON.stringify(planObj, null, 2), 'utf8');

        return `Plan updated successfully. Appended ${newSteps.length} steps.`;

    } catch (e) {
        return `Error updating plan: ${e.message}`;
    }
}

module.exports = updatePlan;
