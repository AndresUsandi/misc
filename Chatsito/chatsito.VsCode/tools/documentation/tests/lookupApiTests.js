const assert = require('assert');
const vscode = require('vscode');
const lookupApi = require('../lookupApi.js');

describe('lookupApi Tool', function () {
    this.timeout(10000);

    let originalExecuteCommand;

    before(() => {
        originalExecuteCommand = vscode.commands.executeCommand;
    });

    afterEach(() => {
        vscode.commands.executeCommand = originalExecuteCommand;
    });

    it('should successfully lookup and format API symbols', async () => {
        // Mock executeCommand to return dummy symbols
        vscode.commands.executeCommand = async (command, query) => {
            if (command === 'vscode.executeWorkspaceSymbolProvider' && query === 'MyClass') {
                return [
                    {
                        name: 'MyClass',
                        kind: 1, // vscode.SymbolKind.File/Class
                        containerName: 'MyNamespace',
                        location: {
                            uri: vscode.Uri.file('/path/to/MyClass.js'),
                            range: { start: { line: 9 } }
                        }
                    }
                ];
            }
            return [];
        };

        const output = await lookupApi('MyClass');
        assert.ok(output.includes('API Lookup Results for "MyClass"'), `Output: ${output}`);
        assert.ok(output.includes('MyClass'));
        assert.ok(output.includes('Container: MyNamespace'));
    });

    it('should return message if no symbols found', async () => {
        vscode.commands.executeCommand = async () => [];
        const output = await lookupApi('UnknownSymbol');
        assert.strictEqual(output, 'No API definitions found for symbol: "UnknownSymbol".');
    });

    it('should return error for missing parameters', async () => {
        const output = await lookupApi('');
        assert.strictEqual(output, 'Error: Missing symbolName parameter.');
    });
});
