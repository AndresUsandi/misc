const assert = require('assert');
const vscode = require('vscode');
const path = require('path');
const getInitialPromptContext = require('../../../ContextBuilder.js');

describe('getInitialPromptContext Tool', function () {
    this.timeout(20000);

    it('should extract enclosing symbol and its caller (references) call stack context in a JS file', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');
        
        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Act: TargetMethod at line 2 (1-based index 2)
        const output = await getInitialPromptContext(fixturePath, 2, 1);
        
        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('=== THE FOLLOWING CONTEXT PROVIDES CODE FOR THE CURRENTLY SELECTED FUNCTION OR CLASS AND THEIR REFERENCES (RECURSIVELY) ==='), 'Should include caller context delimiter');
        assert.ok(output.includes('TargetMethod'), 'Should mention TargetMethod as enclosing symbol');
        assert.ok(output.includes('--- invocation stack level 1 ---'), 'Should include caller context');
        assert.ok(output.includes('CallerMethod'), 'Should mention CallerMethod as caller');
    });

    it('should include callee context recursively in the output', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'TestDefinition.js');

        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Act: CallerMethod is at line 5
        const output = await getInitialPromptContext(fixturePath, 5, 1);

        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('=== THE FOLLOWING CONTEXT PROVIDES CODE FOR THE CURRENTLY SELECTED FUNCTION AND THE FUNCTIONS IT CALLS (RECURSIVELY) ==='), 'Should include callee delimiter');
        assert.ok(output.includes('TargetMethod'), 'Should show TargetMethod as callee');
    });

    it('should include imported files context recursively in the output', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'ImportRoot.js');

        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Act: rootMethod at line 3
        const output = await getInitialPromptContext(fixturePath, 3, 2);

        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('=== THE FOLLOWING CONTEXT PROVIDES FILE PATH FOR THE CURRENTLY SELECTED FILE AND ALL IMPORTED FILES (RECURSIVELY) ==='), 'Should include file context delimiter');
        assert.ok(output.includes('TestDefinition.js'), 'Should resolve and include TestDefinition.js path/content');
    });

    it('should fall back to surrounding 50 lines if no enclosing symbol is found', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'ImportRoot.js');

        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Act: line 1 (outside rootMethod, so no enclosing symbol)
        const output = await getInitialPromptContext(fixturePath, 1, 2);

        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('=== THE FOLLOWING CONTEXT PROVIDES CODE FOR THE CURRENTLY SELECTED FUNCTION OR CLASS AND THEIR REFERENCES (RECURSIVELY) ==='), 'Should include caller context delimiter');
        assert.ok(output.includes('--- original context ---'), 'Should include original context formatting');
        assert.ok(output.includes('const { TargetMethod } = require'), 'Should include line 1 content');
    });

    it('should include project and workspace structure context in the output', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        assert.ok(workspaceFolders && workspaceFolders.length > 0, 'No workspace folder open for test');
        const root = workspaceFolders[0].uri.fsPath;
        const fixturePath = path.join(root, 'test', 'fixtures', 'ImportRoot.js');

        const doc = await vscode.workspace.openTextDocument(vscode.Uri.file(fixturePath));
        await vscode.window.showTextDocument(doc);
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Act: query rootMethod at line 3
        const output = await getInitialPromptContext(fixturePath, 3, 2);

        assert.ok(output, 'Output should not be null');
        assert.ok(output.includes('=== THE FOLLOWING CONTEXT PROVIDES THE PROJECT CONFIGURATION FILES ==='), 'Should include project configuration delimiter');
        assert.ok(output.includes('package.json'), 'Should include package.json content');
        assert.ok(output.includes('=== THE FOLLOWING CONTEXT PROVIDES THE WORKSPACE STRUCTURE SUMMARY ==='), 'Should include workspace structure delimiter');
        assert.ok(output.includes('ImportRoot.js'), 'Should list files in workspace structure');
    });

    it('should return error for empty file path', async () => {
        const output = await getInitialPromptContext('', 1);
        assert.ok(output.includes('Failed to open or resolve context for') || output.includes('No workspace folder open.') || output.includes('Failed to resolve callee context for'), 'Should fail gracefully for empty path');
    });
});
