const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const createTask = require('../createTask.js');

describe('createTask Tool', function () {
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

    it('should successfully create a new task', async () => {
        const output1 = await createTask('My first task');
        assert.ok(output1.includes('Task created successfully with ID 1'), `Output: ${output1}`);
        
        const output2 = await createTask('My second task');
        assert.ok(output2.includes('Task created successfully with ID 2'), `Output: ${output2}`);
        
        const tasksObj = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
        assert.strictEqual(tasksObj.tasks.length, 2);
        assert.strictEqual(tasksObj.tasks[0].description, 'My first task');
        assert.strictEqual(tasksObj.tasks[1].description, 'My second task');
        assert.strictEqual(tasksObj.tasks[0].completed, false);
    });

    it('should return error for missing parameters', async () => {
        const output = await createTask('');
        assert.strictEqual(output, 'Error: Missing description parameter.');
    });
});
