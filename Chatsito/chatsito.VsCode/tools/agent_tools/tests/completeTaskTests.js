const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const completeTask = require('../completeTask.js');
const createTask = require('../createTask.js');

describe('completeTask Tool', function () {
    this.timeout(10000);

    let tasksPath;

    before(() => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const rootPath = workspaceFolders[0].uri.fsPath;
        tasksPath = path.join(rootPath, '.chatsito', 'tasks.json');
    });

    afterEach(() => {
        if (fs.existsSync(tasksPath)) {
            fs.unlinkSync(tasksPath);
        }
    });

    it('should successfully complete an existing task', async () => {
        await createTask('Task 1');
        await createTask('Task 2');
        
        const output = await completeTask(2); // IDs are 1, 2
        assert.ok(output.includes('Task 2 marked as complete'), `Output: ${output}`);
        
        const tasksObj = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
        assert.strictEqual(tasksObj.tasks[0].completed, false);
        assert.strictEqual(tasksObj.tasks[1].completed, true);
    });

    it('should return error if task ID does not exist', async () => {
        await createTask('Task 1');
        const output = await completeTask(99);
        assert.ok(output.includes('Error: Task with ID 99 not found'), `Output: ${output}`);
    });

    it('should return error for missing parameters', async () => {
        const output = await completeTask('');
        assert.strictEqual(output, 'Error: Missing taskId parameter.');
    });
});
