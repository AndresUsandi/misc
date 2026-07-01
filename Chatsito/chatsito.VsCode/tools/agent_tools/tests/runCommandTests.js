const assert = require('assert');
const vscode = require('vscode');
const runCommand = require('../runCommand.js');

describe('runCommand Tool', function () {
    this.timeout(10000);

    it('should execute command', async () => {
        const output = await runCommand('node -e "console.log(\'HELLO COMMAND\')"');
        assert.ok(output.includes('Command Execution Output'), `Output: ${output}`);
        assert.ok(output.includes('HELLO COMMAND'), 'Should capture stdout');
    });

    it('should return error for missing parameters', async () => {
        const output = await runCommand('');
        assert.strictEqual(output, 'Error: No command provided.');
    });
});
