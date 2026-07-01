const vscode = require('vscode');

async function requestUserConfirmation(message) {
    if (!message) return "Error: Missing message parameter.";

    try {
        // Modal true forces the user to interact
        const result = await vscode.window.showInformationMessage(
            String(message),
            { modal: true },
            'Yes',
            'No'
        );

        if (result === 'Yes') {
            return "User confirmed: Yes";
        } else if (result === 'No') {
            return "User denied: No";
        } else {
            return "User dismissed the dialog.";
        }

    } catch (e) {
        return `Error requesting confirmation: ${e.message}`;
    }
}

module.exports = requestUserConfirmation;
