const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const findImplementations = require('../findImplementations.js');

describe('findImplementations Tool', () => {
    let providerDisposable;
    let fixturePath;

    before(async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0);
        fixturePath = path.resolve(workspaceFolders[0].uri.fsPath, 'test/fixtures/mock_file.mock');

        providerDisposable = vscode.languages.registerImplementationProvider(
            { pattern: '**/mock_file.mock' },
            {
                provideImplementation(document, position, token) {
                    if (position.line === 5) {
                        return [
                            new vscode.Location(
                                vscode.Uri.file(fixturePath),
                                new vscode.Range(1, 0, 1, 15)
                            )
                        ];
                    }
                    return [];
                }
            }
        );
    });

    after(() => {
        if (providerDisposable) {
            providerDisposable.dispose();
        }
    });

    it('should find implementations when provider registers them', async () => {
        const output = await findImplementations(fixturePath, 5, 0);
        assert.ok(output.includes('=== Implementations Found'), 'Should contain implementation header');
        assert.ok(output.includes('mock_file.mock:2:1'), 'Should point to correct file, line 2, character 1');
    });

    it('should return no implementations found if provider returns empty', async () => {
        const output = await findImplementations(fixturePath, 0, 0);
        assert.ok(output.includes('No implementations found for symbol'), `Expected no implementations message, got: ${output}`);
    });
});
