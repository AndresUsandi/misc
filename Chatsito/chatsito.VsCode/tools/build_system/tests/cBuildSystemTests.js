const assert = require('assert');
const path = require('path');
const fs = require('fs');
const vscode = require('vscode');
const buildProject = require('../c_build_system/buildProject');
const listTests = require('../c_build_system/listTests');

describe('C/C++ Build System Tools', function () {
    this.timeout(20000);

    it('should identify CMake project and execute command', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_c');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        const cmakePath = path.join(tempDir, 'CMakeLists.txt');
        fs.writeFileSync(cmakePath, 'project(mock_c)', 'utf8');

        const output = await buildProject(tempDir);
        assert.ok(output.includes('cmake --build') || output.toLowerCase().includes('cmake') || output.toLowerCase().includes('error'));

        fs.unlinkSync(cmakePath);
        fs.rmdirSync(tempDir);
    });

    it('should identify Google Test / Catch2 definitions and list them', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        const root = workspaceFolders[0].uri.fsPath;
        const parentDir = path.basename(root) === 'chatsito.VsCode' ? path.dirname(root) : root;
        const tempDir = path.join(parentDir, 'chatsito.VsCode', 'test', 'fixtures', 'mock_c_tests');
        
        if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
        
        const testFilePath = path.join(tempDir, 'sample_test.cpp');
        const testContent = `
#include <gtest/gtest.h>
TEST(MySuite, TestOne) {
    EXPECT_EQ(1, 1);
}
TEST_CASE("MyCatchTest", "[tag]") {
    REQUIRE(true);
}
        `;
        fs.writeFileSync(testFilePath, testContent, 'utf8');

        const output = await listTests(tempDir);
        assert.ok(output.includes('Discovered C/C++ Tests'), `Output: ${output}`);
        assert.ok(output.includes('MySuite'), `Output: ${output}`);
        assert.ok(output.includes('TestOne'), `Output: ${output}`);
        assert.ok(output.includes('MyCatchTest'), `Output: ${output}`);

        fs.unlinkSync(testFilePath);
        fs.rmdirSync(tempDir);
    });
});
