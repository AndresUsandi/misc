const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const updatePlan = require('../updatePlan.js');
const createPlan = require('../createPlan.js');

describe('updatePlan Tool', function () {
    this.timeout(10000);

    let planPath;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const rootPath = workspaceFolders[0].uri.fsPath;
        planPath = path.join(rootPath, '.chatsito', 'plan.json');
    });

    afterEach(() => {
        if (fs.existsSync(planPath)) {
            fs.unlinkSync(planPath);
        }
    });

    it('should successfully append steps to existing plan', async () => {
        await createPlan(['Step 1']);
        
        const output = await updatePlan(['Step 2', 'Step 3']);
        assert.ok(output.includes('Plan updated successfully'), `Output: ${output}`);
        
        const planObj = JSON.parse(fs.readFileSync(planPath, 'utf8'));
        assert.strictEqual(planObj.steps.length, 3);
        assert.strictEqual(planObj.steps[1].description, 'Step 2');
        assert.strictEqual(planObj.steps[2].description, 'Step 3');
    });

    it('should return error if no active plan exists', async () => {
        const output = await updatePlan(['Step 1']);
        assert.strictEqual(output, 'Error: No active plan found. Use createPlan first.');
    });

    it('should return error for missing parameters', async () => {
        const output = await updatePlan();
        assert.strictEqual(output, 'Error: Missing stepsInput parameter.');
    });
});
