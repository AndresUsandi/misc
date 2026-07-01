const assert = require('assert');
const vscode = require('vscode');
const findSymbol = require('../findSymbol.js');

describe('findSymbol Tool', () => {
    let providerDisposable;
    let mockSymbols;

    before(() => {
        mockSymbols = [
            new vscode.SymbolInformation(
                'MyAwesomeClass',
                vscode.SymbolKind.Class,
                'MyNamespace',
                new vscode.Location(vscode.Uri.file('d:/Development/GitHub/MachineLarning/chatsito/chatsito.VSTest/test/fixtures/TestDefinition.js'), new vscode.Range(0, 0, 0, 10))
            ),
            new vscode.SymbolInformation(
                'MyAwesomeMethod',
                vscode.SymbolKind.Method,
                'MyAwesomeClass',
                new vscode.Location(vscode.Uri.file('d:/Development/GitHub/MachineLarning/chatsito/chatsito.VSTest/test/fixtures/TestDefinition.js'), new vscode.Range(5, 0, 5, 20))
            )
        ];

        providerDisposable = vscode.languages.registerWorkspaceSymbolProvider({
            provideWorkspaceSymbols(query) {
                return mockSymbols.filter(s => s.name.toLowerCase().includes(query.toLowerCase()));
            }
        });
    });

    after(() => {
        if (providerDisposable) {
            providerDisposable.dispose();
        }
    });

    it('should find symbols matching name', async () => {
        const output = await findSymbol('MyAwesome');
        assert.ok(output.includes('=== Symbols Found'), 'Should contain the header');
        assert.ok(output.includes('MyAwesomeClass'), 'Should find class symbol');
        assert.ok(output.includes('MyAwesomeMethod'), 'Should find method symbol');
        assert.ok(output.includes('Kind: Class'), 'Should show kind for class');
        assert.ok(output.includes('Kind: Method'), 'Should show kind for method');
    });

    it('should return empty/not-found message when no match', async () => {
        const output = await findSymbol('NonExistentSymbol123');
        assert.strictEqual(output, `No symbols found matching: NonExistentSymbol123`);
    });

    it('should return error if empty name is passed', async () => {
        const output = await findSymbol('');
        assert.strictEqual(output, 'Error: No symbol name provided.');
    });
});
