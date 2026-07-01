const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const markPlanStepComplete = require('../markPlanStepComplete.js');
const createPlan = require('../createPlan.js');

describe('markPlanStepComplete Tool', function () {
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

    it('should successfully mark a step complete', async () => {
        await createPlan(['Step 1', 'Step 2']);
        
        const output = await markPlanStepComplete(1); // 0-based index
        assert.ok(output.includes('Step 1 marked as complete'), `Output: ${output}`);
        
        const planObj = JSON.parse(fs.readFileSync(planPath, 'utf8'));
        assert.strictEqual(planObj.steps[1].completed, true);
        assert.strictEqual(planObj.steps[0].completed, false);
    });

    it('should return error for invalid index', async () => {
        await createPlan(['Step 1']);
        const output = await markPlanStepComplete(5);
        assert.ok(output.includes('Error: Invalid stepIndex'), `Output: ${output}`);
    });

    it('should return error for missing parameters', async () => {
        const output = await markPlanStepComplete('');
        assert.strictEqual(output, 'Error: Missing stepIndex parameter.');
    });
});
