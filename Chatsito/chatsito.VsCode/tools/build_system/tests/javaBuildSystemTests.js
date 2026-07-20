const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildProject = require('../java_build_system/buildProject');
const buildSolution = require('../java_build_system/buildSolution');
const listTests = require('../java_build_system/listTests');

describe('Java Build System Tools', function () {
    this.timeout(20000);

    it('should identify Maven and return build output or execution message', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_java');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        const pomPath = path.join(tempDir, 'pom.xml');
        fs.writeFileSync(pomPath, '<project><modelVersion>4.0.0</modelVersion></project>', 'utf8');

        const output = await buildProject(tempDir);
        assert.ok(output.includes('mvn compile') || output.toLowerCase().includes('mvn') || output.toLowerCase().includes('error'));

        const outputSol = await buildSolution(tempDir);
        assert.ok(outputSol.includes('mvn package') || outputSol.toLowerCase().includes('mvn') || outputSol.toLowerCase().includes('error'));

        fs.unlinkSync(pomPath);
        fs.rmdirSync(tempDir);
    });

    it('should find Java test files and list JUnit tests', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_java_tests');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        
        const testFilePath = path.join(tempDir, 'MySampleTest.java');
        const testContent = `
package com.example;
import org.junit.Test;
public class MySampleTest {
    @Test
    public void testAddition() {
    }
}
        `;
        fs.writeFileSync(testFilePath, testContent, 'utf8');

        const output = await listTests(tempDir);
        assert.ok(output.includes('Discovered Java JUnit Tests'), `Output: ${output}`);
        assert.ok(output.includes('com.example.MySampleTest'), `Output: ${output}`);
        assert.ok(output.includes('testAddition'), `Output: ${output}`);

        fs.unlinkSync(testFilePath);
        fs.rmdirSync(tempDir);
    });
});
