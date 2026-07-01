const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const findBaseTypes = require('../findBaseTypes.js');

describe('findBaseTypes Tool', () => {
    let providerDisposable;
    let fixturePath;

    before(async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0);
        fixturePath = path.resolve(workspaceFolders[0].uri.fsPath, 'test/fixtures/mock_file.mock');

        providerDisposable = vscode.languages.registerTypeHierarchyProvider(
            { pattern: '**/mock_file.mock' },
            {
                prepareTypeHierarchy(document, position, token) {
                    if (position.line === 5) {
                        return [
                            new vscode.TypeHierarchyItem(
                                vscode.SymbolKind.Class,
                                'ChildClass',
                                'MyNamespace',
                                document.uri,
                                new vscode.Range(5, 0, 5, 20),
                                new vscode.Range(5, 0, 5, 20)
                            )
                        ];
                    }
                    return undefined;
                },
                provideTypeHierarchySupertypes(item, token) {
                    if (item && item.name === 'ChildClass') {
                        return [
                            new vscode.TypeHierarchyItem(
                                vscode.SymbolKind.Class,
                                'BaseClass',
                                'MyNamespace',
                                item.uri,
                                new vscode.Range(0, 0, 0, 20),
                                new vscode.Range(0, 0, 0, 20)
                            )
                        ];
                    }
                    return undefined;
                },
                provideTypeHierarchySubtypes(item, token) {
                    return undefined;
                }
            }
        );
    });

    after(() => {
        if (providerDisposable) {
            providerDisposable.dispose();
        }
    });

    it('should find base types when provider registers them', async () => {
        const output = await findBaseTypes(fixturePath, 5, 0);
        console.log("DEBUG findBaseTypes output (line 5):", output);
        assert.ok(output.includes('=== Base Types / Supertypes ==='), 'Should contain header');
        assert.ok(output.includes('Type: ChildClass (Class)'), 'Should print the type name and kind');
        assert.ok(output.includes('- BaseClass'), 'Should print the base type');
    });

    it('should return no hierarchy message when type hierarchy is empty', async () => {
        const output = await findBaseTypes(fixturePath, 0, 0);
        console.log("DEBUG findBaseTypes output (line 0):", output);
        assert.ok(output.includes('No type hierarchy found at'), `Expected no hierarchy message, got: ${output}`);
    });
});
