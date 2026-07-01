const assert = require('assert');
const vscode = require('vscode');
const requestUserConfirmation = require('../requestUserConfirmation.js');

describe('requestUserConfirmation Tool', function () {
    this.timeout(10000);

    let originalShowInformationMessage;

    before(() => {
        originalShowInformationMessage = vscode.window.showInformationMessage;
    });

    afterEach(() => {
        vscode.window.showInformationMessage = originalShowInformationMessage;
    });

    it('should return User confirmed: Yes when user clicks Yes', async () => {
        vscode.window.showInformationMessage = async () => 'Yes';
        const output = await requestUserConfirmation('Are you sure?');
        assert.strictEqual(output, 'User confirmed: Yes');
    });

    it('should return User denied: No when user clicks No', async () => {
        vscode.window.showInformationMessage = async () => 'No';
        const output = await requestUserConfirmation('Are you sure?');
        assert.strictEqual(output, 'User denied: No');
    });

    it('should return User dismissed when dialog is closed', async () => {
        vscode.window.showInformationMessage = async () => undefined;
        const output = await requestUserConfirmation('Are you sure?');
        assert.strictEqual(output, 'User dismissed the dialog.');
    });

    it('should return error for missing parameters', async () => {
        const output = await requestUserConfirmation('');
        assert.strictEqual(output, 'Error: Missing message parameter.');
    });
});
