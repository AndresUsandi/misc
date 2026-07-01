const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

async function markPlanStepComplete(stepIndexStr) {
    if (stepIndexStr === undefined || stepIndexStr === null || stepIndexStr === '') {
        return "Error: Missing stepIndex parameter.";
    }

    const stepIndex = parseInt(stepIndexStr, 10);
    if (isNaN(stepIndex)) {
        return "Error: stepIndex must be a number.";
    }

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
        
        // Use 1-based indexing for user-friendliness if specified, but usually arrays are 0-based
        // Let's assume 0-based index since it's an API, or maybe 1-based. Let's do 0-based.
        if (stepIndex < 0 || stepIndex >= planObj.steps.length) {
            return `Error: Invalid stepIndex ${stepIndex}. Plan has ${planObj.steps.length} steps.`;
        }

        planObj.steps[stepIndex].completed = true;

        fs.writeFileSync(planPath, JSON.stringify(planObj, null, 2), 'utf8');

        return `Step ${stepIndex} marked as complete: "${planObj.steps[stepIndex].description}"`;

    } catch (e) {
        return `Error marking plan step complete: ${e.message}`;
    }
}

module.exports = markPlanStepComplete;
