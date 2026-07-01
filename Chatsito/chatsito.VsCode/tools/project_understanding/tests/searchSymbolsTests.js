const assert = require('assert');
const vscode = require('vscode');
const searchSymbols = require('../searchSymbols.js');

describe('searchSymbols Tool', () => {
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
            ),
            new vscode.SymbolInformation(
                'OtherHelper',
                vscode.SymbolKind.Function,
                'Global',
                new vscode.Location(vscode.Uri.file('d:/Development/GitHub/MachineLarning/chatsito/chatsito.VSTest/test/fixtures/TestDefinition.js'), new vscode.Range(10, 0, 10, 30))
            )
        ];

        providerDisposable = vscode.languages.registerWorkspaceSymbolProvider({
            provideWorkspaceSymbols(query) {
                if (!query || query.trim() === '') {
                    return mockSymbols;
                }
                return mockSymbols.filter(s => s.name.toLowerCase().includes(query.toLowerCase()));
            }
        });
    });

    after(() => {
        if (providerDisposable) {
            providerDisposable.dispose();
        }
    });

    it('should find symbols matching query and apply kind filters', async () => {
        const output = await searchSymbols('MyAwesome kind:method');
        assert.ok(output.includes('=== Symbols Search Results'), 'Should contain search header');
        assert.ok(!output.includes('Symbol: MyAwesomeClass'), 'Should filter out class kind');
        assert.ok(output.includes('MyAwesomeMethod'), 'Should keep method kind');
        assert.ok(output.includes('Kind: Method'), 'Should show kind Method');
    });

    it('should find symbols matching query and apply container filters', async () => {
        const output = await searchSymbols('MyAwesome container:mynamespace');
        assert.ok(output.includes('=== Symbols Search Results'), 'Should contain search header');
        assert.ok(output.includes('MyAwesomeClass'), 'Should keep class container in namespace');
        assert.ok(!output.includes('MyAwesomeMethod'), 'Should filter out method not in namespace');
    });

    it('should return error if empty query is passed', async () => {
        const output = await searchSymbols('');
        assert.strictEqual(output, 'Error: No query provided.');
    });

    it('should return empty search message when nothing matches filters', async () => {
        const output = await searchSymbols('Helper kind:class');
        assert.strictEqual(output, 'No symbols found matching query: Helper kind:class');
    });
});
