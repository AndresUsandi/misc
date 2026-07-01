const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const createPlan = require('../createPlan.js');

describe('createPlan Tool', function () {
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

    it('should successfully create a plan from an array', async () => {
        const steps = ['Step 1', 'Step 2', 'Step 3'];
        const output = await createPlan(steps);
        
        assert.ok(output.includes('Plan created successfully with 3 steps'), `Output: ${output}`);
        
        assert.ok(fs.existsSync(planPath), 'plan.json should be created');
        const planObj = JSON.parse(fs.readFileSync(planPath, 'utf8'));
        assert.strictEqual(planObj.steps.length, 3);
        assert.strictEqual(planObj.steps[0].description, 'Step 1');
        assert.strictEqual(planObj.steps[0].completed, false);
    });

    it('should successfully create a plan from a string', async () => {
        const stepsStr = 'Line 1\nLine 2';
        const output = await createPlan(stepsStr);
        
        assert.ok(output.includes('Plan created successfully with 2 steps'), `Output: ${output}`);
        
        const planObj = JSON.parse(fs.readFileSync(planPath, 'utf8'));
        assert.strictEqual(planObj.steps.length, 2);
    });

    it('should return error for missing parameters', async () => {
        const output = await createPlan();
        assert.strictEqual(output, 'Error: Missing stepsInput parameter.');
    });
});
