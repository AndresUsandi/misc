const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const findCallers = require('../findCallers.js');

describe('findCallers Tool', () => {
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
                    if (item && item.name === 'TargetMethod') {
                        const callerItem = new vscode.CallHierarchyItem(
                            vscode.SymbolKind.Method,
                            'CallerMethod',
                            'OtherClass',
                            item.uri,
                            new vscode.Range(15, 0, 15, 20),
                            new vscode.Range(15, 0, 15, 20)
                        );
                        return [
                            new vscode.CallHierarchyIncomingCall(
                                callerItem,
                                [new vscode.Range(17, 0, 17, 10)]
                            )
                        ];
                    }
                    return undefined;
                },
                provideCallHierarchyOutgoingCalls(item, token) {
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

    it('should find callers when provider registers them', async () => {
        const output = await findCallers(fixturePath, 5, 0);
        console.log("DEBUG findCallers output (line 5):", output);
        assert.ok(output.includes('=== Callers / Incoming Calls ==='), 'Should contain header');
        assert.ok(output.includes('Symbol: TargetMethod (Method)'), 'Should print the symbol name and kind');
        assert.ok(output.includes('- CallerMethod'), 'Should print the caller method');
        assert.ok(output.includes('at: line 18'), 'Should show call range line 18 (1-indexed from 17)');
    });

    it('should return no call hierarchy message when hierarchy is empty', async () => {
        const output = await findCallers(fixturePath, 0, 0);
        console.log("DEBUG findCallers output (line 0):", output);
        assert.ok(output.includes('No call hierarchy found at'), `Expected no hierarchy message, got: ${output}`);
    });
});
