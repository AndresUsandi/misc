const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const findCallees = require('../findCallees.js');

describe('findCallees Tool', () => {
    let providerDisposable;
    let fixturePath;

    before(async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0);
        fixturePath = path.resolve(workspaceFolders[0].uri.fsPath, 'test/fixtures/mock_file.mock');

        providerDisposable = vscode.languages.registerCallHierarchyProvider(
            { pattern: '**/mock_file.mock' },
            {
                prepareCallHierarchy(document, position, token) {
                    if (position.line === 5) {
                        return [
                            new vscode.CallHierarchyItem(
                                vscode.SymbolKind.Method,
                                'TargetMethod',
                                'MyClass',
                                document.uri,
                                new vscode.Range(5, 0, 5, 20),
                                new vscode.Range(5, 0, 5, 20)
                            )
                        ];
                    }
                    return undefined;
                },
                provideCallHierarchyIncomingCalls(item, token) {
                    return undefined;
                },
                provideCallHierarchyOutgoingCalls(item, token) {
                    if (item && item.name === 'TargetMethod') {
                        const calleeItem = new vscode.CallHierarchyItem(
                            vscode.SymbolKind.Method,
                            'CalleeMethod',
                            'OtherClass',
                            item.uri,
                            new vscode.Range(25, 0, 25, 20),
                            new vscode.Range(25, 0, 25, 20)
                        );
                        return [
                            new vscode.CallHierarchyOutgoingCall(
                                calleeItem,
                                [new vscode.Range(7, 0, 7, 10)]
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

    it('should find callees when provider registers them', async () => {
        const output = await findCallees(fixturePath, 5, 0);
        console.log("DEBUG findCallees output (line 5):", output);
        assert.ok(output.includes('=== Callees / Outgoing Calls ==='), 'Should contain header');
        assert.ok(output.includes('Symbol: TargetMethod (Method)'), 'Should print the symbol name and kind');
        assert.ok(output.includes('- CalleeMethod'), 'Should print the callee method');
        assert.ok(output.includes('at: line 8'), 'Should show call range line 8 (1-indexed from 7)');
    });

    it('should return no call hierarchy message when hierarchy is empty', async () => {
        const output = await findCallees(fixturePath, 0, 0);
        console.log("DEBUG findCallees output (line 0):", output);
        assert.ok(output.includes('No call hierarchy found at'), `Expected no hierarchy message, got: ${output}`);
    });
});
