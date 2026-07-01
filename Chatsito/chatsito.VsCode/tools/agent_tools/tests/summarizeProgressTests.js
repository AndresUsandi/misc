const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const summarizeProgress = require('../summarizeProgress.js');
const createPlan = require('../createPlan.js');
const createTask = require('../createTask.js');
const completeTask = require('../completeTask.js');
const markPlanStepComplete = require('../markPlanStepComplete.js');

describe('summarizeProgress Tool', function () {
    this.timeout(15000);

    let chatsitoDir;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const rootPath = workspaceFolders[0].uri.fsPath;
        chatsitoDir = path.join(rootPath, '.chatsito');
    });

    afterEach(() => {
        if (fs.existsSync(path.join(chatsitoDir, 'plan.json'))) {
            fs.unlinkSync(path.join(chatsitoDir, 'plan.json'));
        }
        if (fs.existsSync(path.join(chatsitoDir, 'tasks.json'))) {
            fs.unlinkSync(path.join(chatsitoDir, 'tasks.json'));
        }
    });

    it('should successfully summarize plan and tasks', async () => {
        await createPlan(['First Step', 'Second Step']);
        await markPlanStepComplete(0);
        
        await createTask('My Task A');
        await createTask('My Task B');
        await completeTask(2); // Second task ID is 2
        
        const output = await summarizeProgress();
        
        assert.ok(output.includes('Progress Summary'), `Output: ${output}`);
        assert.ok(output.includes('Plan Progress (1/2 completed)'), 'Should report plan progress');
        assert.ok(output.includes('[x] Step 0: First Step'), 'Should show completed step');
        assert.ok(output.includes('[ ] Step 1: Second Step'), 'Should show uncompleted step');
        
        assert.ok(output.includes('Tasks Progress (1/2 completed)'), 'Should report tasks progress');
        assert.ok(output.includes('[ ] Task 1: My Task A'), 'Should show uncompleted task');
        assert.ok(output.includes('[x] Task 2: My Task B'), 'Should show completed task');
    });

    it('should report no active plan/tasks if none exist', async () => {
        const output = await summarizeProgress();
        assert.ok(output.includes('No active plan.'));
        assert.ok(output.includes('No active tasks.'));
    });
});
