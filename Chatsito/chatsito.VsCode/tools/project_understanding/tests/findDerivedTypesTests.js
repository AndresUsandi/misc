const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const findDerivedTypes = require('../findDerivedTypes.js');

describe('findDerivedTypes Tool', () => {
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
                                'BaseClass',
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
                    return undefined;
                },
                provideTypeHierarchySubtypes(item, token) {
                    if (item && item.name === 'BaseClass') {
                        return [
                            new vscode.TypeHierarchyItem(
                                vscode.SymbolKind.Class,
                                'ChildClass',
                                'MyNamespace',
                                item.uri,
                                new vscode.Range(10, 0, 10, 20),
                                new vscode.Range(10, 0, 10, 20)
                            )
                        ];
                    }
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

    it('should find derived types when provider registers them', async () => {
        const output = await findDerivedTypes(fixturePath, 5, 0);
        console.log("DEBUG findDerivedTypes output (line 5):", output);
        assert.ok(output.includes('=== Derived Types / Subtypes ==='), 'Should contain header');
        assert.ok(output.includes('Type: BaseClass (Class)'), 'Should print the type name and kind');
        assert.ok(output.includes('- ChildClass'), 'Should print the derived type');
    });

    it('should return no hierarchy message when type hierarchy is empty', async () => {
        const output = await findDerivedTypes(fixturePath, 0, 0);
        console.log("DEBUG findDerivedTypes output (line 0):", output);
        assert.ok(output.includes('No type hierarchy found at'), `Expected no hierarchy message, got: ${output}`);
    });
});
